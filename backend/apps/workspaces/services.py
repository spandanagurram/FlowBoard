from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers
from apps.workspaces.tasks import send_workspace_invitation_email

from .models import (
    InvitationRole,
    InvitationStatus,
    Role,
    Workspace,
    WorkspaceInvitation,
    WorkspaceMember
)


User = get_user_model()


class WorkspaceService:
    @staticmethod
    def create_workspace(owner, validated_data):
        try:
            with transaction.atomic():
                workspace = Workspace.objects.create(
                    owner=owner,
                    **validated_data,
                )
                WorkspaceMember.objects.create(
                    workspace=workspace,
                    user=owner,
                    role=Role.OWNER,
                    invited_by=None,
                    is_active=True,
                )
                return workspace
        except IntegrityError as exc:
            name = validated_data.get("name", "")
            if Workspace.objects.filter(owner=owner, name__iexact=name).exists():
                raise serializers.ValidationError(
                    {"name": "You already have a workspace with this name."}
                ) from exc
            raise


class InvitationService:

    STATUS_MESSAGES = {
    InvitationStatus.ACCEPTED: "You have already accepted this invitation.",
    InvitationStatus.REJECTED: "You have already rejected this invitation.",
    InvitationStatus.REVOKED: "This invitation has been revoked.",
    InvitationStatus.EXPIRED: "This invitation has expired.",
    }

    @staticmethod
    def create_invitation(requester, workspace_id, validated_data):
        with transaction.atomic():
            # Fetch the workspace before checking workspace-scoped permissions.
            workspace = Workspace.objects.filter(id=workspace_id).first()
            if workspace is None:
                raise serializers.ValidationError("Workspace not found.")

            # Confirm the requester is an active member of this workspace.
            requester_membership = WorkspaceMember.objects.filter(
                workspace=workspace,
                user=requester,
                is_active=True,
            ).first()
            if requester_membership is None:
                raise serializers.ValidationError(
                    "You are not a member of this workspace."
                )

            # Enforce role-based invitation permissions.
            invitation_role = validated_data["role"]
            if requester_membership.role == Role.OWNER:
                allowed_roles = {
                    InvitationRole.ADMIN,
                    InvitationRole.MEMBER,
                    InvitationRole.VIEWER,
                }
            elif requester_membership.role == Role.ADMIN:
                allowed_roles = {
                    InvitationRole.MEMBER,
                    InvitationRole.VIEWER,
                }
            else:
                raise serializers.ValidationError(
                    "You do not have permission to invite workspace members."
                )

            if invitation_role not in allowed_roles:
                raise serializers.ValidationError(
                    "You do not have permission to invite users with this role."
                )

            # Prevent users from inviting themselves to a workspace.
            invitation_email = validated_data["email"]
            if requester.email == invitation_email:
                raise serializers.ValidationError("You cannot invite yourself.")

            # Check whether an existing FlowBoard user is already an active member.
            invited_user = User.objects.filter(email__iexact=invitation_email).first()
            if invited_user is not None:
                active_membership_exists = WorkspaceMember.objects.filter(
                    workspace=workspace,
                    user=invited_user,
                    is_active=True,
                ).exists()
                if active_membership_exists:
                    raise serializers.ValidationError("User is already a member.")
            
            # Expire stale pending invitations for this workspace and email.
            now = timezone.now()

            WorkspaceInvitation.objects.filter(
                workspace=workspace,
                email=invitation_email,
                status=InvitationStatus.PENDING,
                expires_at__lte=now,
            ).update(
                status=InvitationStatus.EXPIRED,
                updated_at=now,
            )

            # Prevent duplicate pending invitations for the same workspace and email.
            pending_invitation_exists = WorkspaceInvitation.objects.filter(
                workspace=workspace,
                email=invitation_email,
                status=InvitationStatus.PENDING,
            ).exists()
            if pending_invitation_exists:
                raise serializers.ValidationError("Invitation already pending.")

            # Create the workspace invitation.
            invitation = WorkspaceInvitation.objects.create(
                workspace=workspace,
                email=invitation_email,
                role=invitation_role,
                invited_by=requester,
            )
            send_workspace_invitation_email.delay(str(invitation.id))
            return invitation

    @staticmethod
    def accept_invitation(token, user):
        with transaction.atomic():
            # Find the invitation by its secure token.
            invitation = WorkspaceInvitation.objects.filter(token=token).first()
            if invitation is None:
                raise serializers.ValidationError("Invitation not found.")

            # Only pending invitations can be accepted.
            if invitation.status != InvitationStatus.PENDING:
                raise serializers.ValidationError(
                    InvitationService.STATUS_MESSAGES.get(
                        invitation.status,
                        "Invitation is no longer pending.",
                    )
                )

            # Expire stale invitations before rejecting the accept attempt.
            now = timezone.now()
            if invitation.expires_at <= now:
                raise serializers.ValidationError("Invitation has expired.")

            # Ensure the authenticated user owns the invited email address.
            if user.email != invitation.email:
                raise serializers.ValidationError(
                    "This invitation does not belong to your account."
                )

            # Prevent accepting an invitation after the user is already active.
            membership = WorkspaceMember.objects.filter(
                workspace=invitation.workspace,
                user=user,
            ).first()
            if membership is not None:
                if membership.is_active:
                    raise serializers.ValidationError("User is already a member.")

                # Reactivate an existing inactive membership if one is present.
                membership.is_active = True
                membership.role = invitation.role
                membership.joined_at = now
                membership.save(
                    update_fields=["is_active", "role", "joined_at", "updated_at"]
                )
            else:
                # Create a new active workspace membership for first-time members.
                WorkspaceMember.objects.create(
                    workspace=invitation.workspace,
                    user=user,
                    role=invitation.role,
                    invited_by=invitation.invited_by,
                    is_active=True,
                    joined_at=now,
                )

            # Mark the invitation as accepted once membership is active.
            invitation.status = InvitationStatus.ACCEPTED
            invitation.accepted_at = now
            invitation.save(update_fields=["status", "accepted_at", "updated_at"])
            return invitation

    @staticmethod
    def reject_invitation(token, user):
        with transaction.atomic():
            # Find the invitation by its secure token.
            invitation = WorkspaceInvitation.objects.filter(token=token).first()
            if invitation is None:
                raise serializers.ValidationError("Invitation not found.")

            # Only pending invitations can be rejected.
            if invitation.status != InvitationStatus.PENDING:
                raise serializers.ValidationError(
                    InvitationService.STATUS_MESSAGES.get(
                        invitation.status,
                        "Invitation is no longer pending.",
                    )
                )

            # Ensure the authenticated user owns the invited email address.
            if user.email != invitation.email:
                raise serializers.ValidationError(
                    "This invitation does not belong to your account."
                )

            # Mark the pending invitation as rejected.
            invitation.status = InvitationStatus.REJECTED
            invitation.save(update_fields=["status", "updated_at"])
            return invitation

    @staticmethod
    def revoke_invitation(invitation_id, requester):
        with transaction.atomic():
            # Find the invitation that should be revoked.
            invitation = WorkspaceInvitation.objects.filter(id=invitation_id).first()
            if invitation is None:
                raise serializers.ValidationError("Invitation not found.")

            # Only pending invitations can be revoked.
            if invitation.status != InvitationStatus.PENDING:
                raise serializers.ValidationError(
                    InvitationService.STATUS_MESSAGES.get(
                        invitation.status,
                        "Invitation is no longer pending.",
                    )
                )

            # Confirm the requester is an active member of this workspace.
            requester_membership = WorkspaceMember.objects.filter(
                workspace=invitation.workspace,
                user=requester,
                is_active=True,
            ).first()
            if requester_membership is None:
                raise serializers.ValidationError(
                    "You are not a member of this workspace."
                )

            # Enforce owner/admin revoke permissions.
            if requester_membership.role == Role.OWNER:
                can_revoke = True
            elif requester_membership.role == Role.ADMIN:
                can_revoke = invitation.invited_by_id == requester.id
            else:
                can_revoke = False

            if not can_revoke:
                raise serializers.ValidationError(
                    "You do not have permission to revoke this invitation."
                )

            # Mark the pending invitation as revoked.
            invitation.status = InvitationStatus.REVOKED
            invitation.save(update_fields=["status", "updated_at"])
            return invitation
    
    @staticmethod
    def expire_pending_invitations() -> int:
        """
        Expire all pending invitations whose expiry time has passed.

        Returns:
            int: Number of invitations expired.
        """
        now = timezone.now()

        return WorkspaceInvitation.objects.filter(
            status=InvitationStatus.PENDING,
            expires_at__lte=now,
        ).update(
            status=InvitationStatus.EXPIRED,
            updated_at=now,
    )
