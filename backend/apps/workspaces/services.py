from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from apps.workspaces.tasks import send_workspace_invitation_email
from apps.activities.models import ActivityAction
from apps.activities.services import ActivityLogService
from apps.common.cache import delete_dashboard_cache

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
    WORKSPACE_ORDERING_FIELDS = {"created_at", "updated_at", "name"}

    @staticmethod
    def _get_active_membership(workspace, requester, lock=False):
        memberships = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=requester,
            is_active=True,
        ).select_related("user", "workspace")
        if lock:
            memberships = memberships.select_for_update()
        return memberships.first()

    @staticmethod
    def _ensure_active_member(workspace, requester, lock=False):
        membership = WorkspaceService._get_active_membership(
            workspace=workspace,
            requester=requester,
            lock=lock,
        )
        if membership is None:
            raise serializers.ValidationError(
                "You are not a member of this workspace."
            )
        return membership

    @staticmethod
    def _ensure_owner(workspace, requester, lock=False):
        membership = WorkspaceService._ensure_active_member(
            workspace=workspace,
            requester=requester,
            lock=lock,
        )
        if membership.role != Role.OWNER:
            raise serializers.ValidationError(
                "You do not have permission to manage this workspace."
            )
        return membership

    @staticmethod
    def _get_active_workspace(workspace_id, lock=False):
        workspaces = Workspace.objects.select_related("owner").filter(
            id=workspace_id,
            is_deleted=False,
        )
        if lock:
            workspaces = workspaces.select_for_update()

        workspace = workspaces.first()
        if workspace is None:
            raise NotFound("Workspace not found.")
        return workspace

    @staticmethod
    def create_workspace(owner, validated_data):
        try:
            with transaction.atomic():
                name = validated_data["name"].strip()
                if Workspace.objects.filter(
                    name__iexact=name,
                    is_deleted=False,
                ).exists():
                    raise serializers.ValidationError(
                        {"name": "Workspace name already exists."}
                    )

                workspace = Workspace.objects.create(
                    owner=owner,
                    name=name,
                    description=validated_data.get("description", ""),
                    logo=validated_data.get("logo"),
                    updated_by=owner,
                )
                
                WorkspaceMember.objects.create(
                    workspace=workspace,
                    user=owner,
                    role=Role.OWNER,
                    invited_by=None,
                    is_active=True,
                )
                ActivityLogService.log_activity(
                    workspace=workspace,
                    actor=owner,
                    action=ActivityAction.WORKSPACE_CREATED,
                    description=(
                        f"{ActivityLogService.get_actor_name(owner)} created "
                        f"workspace {workspace.name}."
                    ),
                    entity_type="workspace",
                    entity_id=workspace.id,
                )
                delete_dashboard_cache(owner.id)
                return workspace
        except IntegrityError as exc:
            name = validated_data.get("name", "")
            if Workspace.objects.filter(
                name__iexact=name,
                is_deleted=False,
            ).exists():
                raise serializers.ValidationError(
                    {"name": "Workspace name already exists."}
                ) from exc
            raise

    @staticmethod
    def list_workspaces(requester, search=None, ordering=None):
        workspaces = Workspace.objects.select_related("owner").filter(
            members__user=requester,
            members__is_active=True,
            is_deleted=False,
        ).distinct()

        if search:
            workspaces = workspaces.filter(name__icontains=search.strip())

        ordering_fields = WorkspaceService._get_ordering_fields(ordering)
        return workspaces.order_by(*ordering_fields)

    @staticmethod
    def list_members(requester, workspace_id):
        workspace = WorkspaceService._get_active_workspace(workspace_id=workspace_id)
        WorkspaceService._ensure_active_member(
            workspace=workspace,
            requester=requester,
        )
        requester_membership = WorkspaceService._ensure_active_member(
            workspace=workspace,
            requester=requester,
        )

        members = (
            WorkspaceMember.objects.select_related("user")
            .filter(
                workspace=workspace,
                is_active=True,
            ).order_by("user__username")
        )

        return requester_membership, members

    @staticmethod
    def get_workspace_detail(requester, workspace_id):
        workspace = WorkspaceService._get_active_workspace(workspace_id=workspace_id)
        WorkspaceService._ensure_active_member(
            workspace=workspace,
            requester=requester,
        )
        return workspace

    @staticmethod
    def update_workspace(requester, workspace_id, validated_data):
        with transaction.atomic():
            workspace = WorkspaceService._get_active_workspace(
                workspace_id=workspace_id,
                lock=True,
            )
            WorkspaceService._ensure_owner(
                workspace=workspace,
                requester=requester,
            )

            update_fields = ["updated_by", "updated_at"]
            if "name" in validated_data:
                name = validated_data["name"].strip()
                if Workspace.objects.filter(
                    name__iexact=name,
                    is_deleted=False,
                ).exclude(id=workspace.id).exists():
                    raise serializers.ValidationError(
                        {"name": "Workspace name already exists."}
                    )
                workspace.name = name
                update_fields.append("name")

            if "description" in validated_data:
                workspace.description = validated_data["description"]
                update_fields.append("description")

            workspace.updated_by = requester
            workspace.save(update_fields=update_fields)
            ActivityLogService.log_activity(
                workspace=workspace,
                actor=requester,
                action=ActivityAction.WORKSPACE_UPDATED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} updated "
                    f"workspace {workspace.name}."
                ),
                entity_type="workspace",
                entity_id=workspace.id,
            )
            return workspace

    @staticmethod
    def soft_delete_workspace(requester, workspace_id):
        with transaction.atomic():
            workspace = WorkspaceService._get_active_workspace(
                workspace_id=workspace_id,
                lock=True,
            )
            WorkspaceService._ensure_owner(
                workspace=workspace,
                requester=requester,
            )

            workspace.is_deleted = True
            workspace.deleted_at = timezone.now()
            workspace.deleted_by = requester
            workspace.updated_by = requester
            workspace.save(
                update_fields=[
                    "is_deleted",
                    "deleted_at",
                    "deleted_by",
                    "updated_by",
                    "updated_at",
                ]
            )
            ActivityLogService.log_activity(
                workspace=workspace,
                actor=requester,
                action=ActivityAction.WORKSPACE_DELETED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} deleted "
                    f"workspace {workspace.name}."
                ),
                entity_type="workspace",
                entity_id=workspace.id,
            )
            delete_dashboard_cache(requester.id)

    @staticmethod
    def transfer_ownership(requester, workspace_id, validated_data):
        with transaction.atomic():
            workspace = WorkspaceService._get_active_workspace(
                workspace_id=workspace_id,
                lock=True,
            )
            old_owner_membership = WorkspaceService._ensure_owner(
                workspace=workspace,
                requester=requester,
                lock=True,
            )

            target_user_id = validated_data["user_id"]
            if target_user_id == requester.id:
                raise serializers.ValidationError(
                    {"user_id": "Current owner cannot be the target user."}
                )

            target_user = User.objects.filter(id=target_user_id).first()
            if target_user is None:
                raise serializers.ValidationError({"user_id": "Target user not found."})

            target_membership = WorkspaceMember.objects.select_for_update().filter(
                workspace=workspace,
                user=target_user,
                is_active=True,
            ).first()
            if target_membership is None:
                raise serializers.ValidationError(
                    {"user_id": "Target user must be an active member of this workspace."}
                )

            if target_membership.role == Role.OWNER:
                raise serializers.ValidationError(
                    {"user_id": "Target user is already the owner."}
                )

            old_owner_membership.role = Role.ADMIN
            old_owner_membership.save(update_fields=["role", "updated_at"])

            target_membership.role = Role.OWNER
            target_membership.save(update_fields=["role", "updated_at"])

            workspace.owner = target_user
            workspace.updated_by = requester
            workspace.save(update_fields=["owner", "updated_by", "updated_at"])
            ActivityLogService.log_activity(
                workspace=workspace,
                actor=requester,
                action=ActivityAction.WORKSPACE_TRANSFERRED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} transferred "
                    f"workspace ownership to "
                    f"{ActivityLogService.get_actor_name(target_user)}."
                ),
                entity_type="workspace",
                entity_id=workspace.id,
                metadata={"old_owner": str(requester.id), "new_owner": str(target_user.id)},
            )
            return workspace

    @staticmethod
    def change_member_role(requester, workspace_id, user_id, validated_data):
        with transaction.atomic():
            workspace = WorkspaceService._get_active_workspace(
                workspace_id=workspace_id,
                lock=True,
            )
            requester_membership = WorkspaceService._ensure_active_member(
                workspace=workspace,
                requester=requester,
                lock=True,
            )

            target_role = validated_data["role"]
            if target_role == Role.OWNER:
                raise serializers.ValidationError(
                    {"role": "Owner role cannot be assigned from this endpoint."}
                )

            if user_id == requester.id:
                raise serializers.ValidationError(
                    {"user_id": "You cannot change your own role."}
                )

            target_user = User.objects.filter(id=user_id).first()
            if target_user is None:
                raise serializers.ValidationError({"user_id": "Target user not found."})

            target_membership = WorkspaceMember.objects.select_for_update().filter(
                workspace=workspace,
                user=target_user,
            ).select_related("user", "workspace").first()
            if target_membership is None:
                raise serializers.ValidationError(
                    {"user_id": "Target user is not a member of this workspace."}
                )

            if not target_membership.is_active:
                raise serializers.ValidationError(
                    {"user_id": "Target user must be an active member of this workspace."}
                )

            WorkspaceService._ensure_can_change_member_role(
                requester_membership=requester_membership,
                target_membership=target_membership,
                target_role=target_role,
            )

            old_role = target_membership.role
            target_membership.role = target_role
            target_membership.save(update_fields=["role", "updated_at"])
            ActivityLogService.log_activity(
                workspace=workspace,
                actor=requester,
                action=ActivityAction.MEMBER_ROLE_CHANGED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} changed "
                    f"{ActivityLogService.get_actor_name(target_user)}'s role from "
                    f"{ActivityLogService.get_role_label(old_role)} to "
                    f"{ActivityLogService.get_role_label(target_role)}."
                ),
                entity_type="workspace_member",
                entity_id=target_membership.id,
                metadata={"old_role": old_role, "new_role": target_role},
            )
            return target_membership

    @staticmethod
    def remove_member(requester, workspace_id, member_id):
        with transaction.atomic():
            workspace = WorkspaceService._get_active_workspace(
                workspace_id=workspace_id,
                lock=True,
            )
            requester_membership = WorkspaceService._ensure_active_member(
                workspace=workspace,
                requester=requester,
                lock=True,
            )

            target_membership = WorkspaceMember.objects.select_for_update().filter(
                id=member_id,
                workspace=workspace,
            ).select_related("user", "workspace").first()
            if target_membership is None:
                raise serializers.ValidationError(
                    {"member_id": "Target member is not a member of this workspace."}
                )

            if not target_membership.is_active:
                raise serializers.ValidationError(
                    {"member_id": "Target member must be an active member of this workspace."}
                )

            if target_membership.user_id == requester.id:
                raise serializers.ValidationError(
                    {"member_id": "You cannot remove yourself from the workspace."}
                )

            WorkspaceService._ensure_can_remove_member(
                requester_membership=requester_membership,
                target_membership=target_membership,
            )

            target_membership.is_active = False
            target_membership.save(update_fields=["is_active"])
            ActivityLogService.log_activity(
                workspace=workspace,
                actor=requester,
                action=ActivityAction.MEMBER_REMOVED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} removed "
                    f"{ActivityLogService.get_actor_name(target_membership.user)} "
                    "from the workspace."
                ),
                entity_type="workspace_member",
                entity_id=target_membership.id,
            )

    @staticmethod
    def _ensure_can_remove_member(requester_membership, target_membership):
        if target_membership.role == Role.OWNER:
            raise serializers.ValidationError(
                "Workspace owner cannot be removed."
            )

        if requester_membership.role == Role.OWNER:
            return

        if (
            requester_membership.role == Role.ADMIN
            and target_membership.role in {Role.MEMBER, Role.VIEWER}
        ):
            return

        raise serializers.ValidationError(
            "You do not have permission to remove this member."
        )

    @staticmethod
    def _ensure_can_change_member_role(
        requester_membership,
        target_membership,
        target_role,
    ):
        if target_membership.role == Role.OWNER:
            raise serializers.ValidationError(
                "Owner role cannot be changed from this endpoint."
            )

        if requester_membership.role == Role.OWNER:
            return

        if requester_membership.role == Role.ADMIN:
            if target_membership.role == Role.ADMIN:
                raise serializers.ValidationError(
                    "Admins cannot modify other admins."
                )

            if target_role == Role.ADMIN:
                raise serializers.ValidationError(
                    {"role": "Admins cannot assign admin role."}
                )

            if target_membership.role in {Role.MEMBER, Role.VIEWER} and target_role in {
                Role.MEMBER,
                Role.VIEWER,
            }:
                return

        raise serializers.ValidationError(
            "You do not have permission to change this member role."
        )

    @staticmethod
    def _get_ordering_fields(ordering):
        if not ordering:
            return ["-created_at"]

        ordering_fields = []
        for field in ordering.split(","):
            field = field.strip()
            if not field:
                continue

            field_name = field[1:] if field.startswith("-") else field
            if field_name not in WorkspaceService.WORKSPACE_ORDERING_FIELDS:
                raise serializers.ValidationError(
                    {"ordering": "Invalid workspace ordering field."}
                )
            ordering_fields.append(field)

        return ordering_fields or ["-created_at"]


class InvitationService:

    STATUS_MESSAGES = {
    InvitationStatus.ACCEPTED: "You have already accepted this invitation.",
    InvitationStatus.REJECTED: "You have already rejected this invitation.",
    InvitationStatus.REVOKED: "This invitation has been revoked.",
    InvitationStatus.EXPIRED: "This invitation has expired.",
    }
    
    @staticmethod
    def _expire_invitation_if_needed(invitation):
        """
        Expire the invitation if it is still pending and has passed its expiry time.
        """
        if (
            invitation.status == InvitationStatus.PENDING
            and invitation.expires_at <= timezone.now()
        ):
            invitation.status = InvitationStatus.EXPIRED
            invitation.save(update_fields=["status", "updated_at"])

            ActivityLogService.log_activity(
                workspace=invitation.workspace,
                actor=None,
                action=ActivityAction.INVITATION_EXPIRED,
                description=f"Invitation for {invitation.email} expired.",
                entity_type="workspace_invitation",
                entity_id=invitation.id,
                metadata={
                    "email": invitation.email,
                    "role": invitation.role,
                },
            )

    @staticmethod
    def create_invitation(requester, workspace_id, validated_data):
        with transaction.atomic():
            # Fetch the workspace before checking workspace-scoped permissions.
            workspace = Workspace.objects.filter(
                id=workspace_id,
                is_deleted=False,
            ).first()
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
            ActivityLogService.log_activity(
                workspace=workspace,
                actor=requester,
                action=ActivityAction.INVITATION_SENT,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} invited "
                    f"{invitation.email} as "
                    f"{ActivityLogService.get_role_label(invitation.role)}."
                ),
                entity_type="workspace_invitation",
                entity_id=invitation.id,
                metadata={"email": invitation.email, "role": invitation.role},
            )
            send_workspace_invitation_email.delay(str(invitation.id))
            return invitation
        
    @staticmethod
    def get_invitation(token):
        with transaction.atomic():
            # Find the invitation by its secure token.
            invitation = (
                WorkspaceInvitation.objects.select_related("workspace")
                .filter(
                    token=token,
                    workspace__is_deleted=False,
                )
                .first()
            )

            if invitation is None:
                raise serializers.ValidationError("Invitation not found.")

            InvitationService._expire_invitation_if_needed(invitation)

            return invitation

    @staticmethod
    def accept_invitation(token, user):
        # Find the invitation by its secure token.
        invitation = (
            WorkspaceInvitation.objects.select_related(
                "workspace",
                "invited_by",
            )
            .filter(
                token=token,
                workspace__is_deleted=False,
            )
            .first()
        )
        if invitation is None:
            raise serializers.ValidationError("Invitation not found.")

        InvitationService._expire_invitation_if_needed(invitation)

        with transaction.atomic():
            # Only pending invitations can be accepted.
            if invitation.status != InvitationStatus.PENDING:
                raise serializers.ValidationError(
                    InvitationService.STATUS_MESSAGES.get(
                        invitation.status,
                        "Invitation is no longer pending.",
                    )
                )

            now = timezone.now()

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
            ActivityLogService.log_activity(
                workspace=invitation.workspace,
                actor=user,
                action=ActivityAction.INVITATION_ACCEPTED,
                description=(
                    f"{ActivityLogService.get_actor_name(user)} accepted the invitation."
                ),
                entity_type="workspace_invitation",
                entity_id=invitation.id,
                metadata={"email": invitation.email, "role": invitation.role},
            )
            return invitation

    @staticmethod
    def reject_invitation(token, user):
        # Find the invitation by its secure token.
        invitation = (
            WorkspaceInvitation.objects.select_related(
                "workspace",
            )
            .filter(
                token=token,
                workspace__is_deleted=False,
            )
            .first()
        )
        if invitation is None:
            raise serializers.ValidationError("Invitation not found.")

        InvitationService._expire_invitation_if_needed(invitation)

        with transaction.atomic():
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
            ActivityLogService.log_activity(
                workspace=invitation.workspace,
                actor=user,
                action=ActivityAction.INVITATION_REJECTED,
                description=(
                    f"{ActivityLogService.get_actor_name(user)} rejected the invitation."
                ),
                entity_type="workspace_invitation",
                entity_id=invitation.id,
                metadata={"email": invitation.email, "role": invitation.role},
            )
            return invitation
    
    @staticmethod
    def revoke_invitation(invitation_id, requester):
        # Find the invitation that should be revoked.
        invitation = (
            WorkspaceInvitation.objects.select_related(
                "workspace",
                "invited_by",
            )
            .filter(
                id=invitation_id,
                workspace__is_deleted=False,
            )
            .first()
        )
        if invitation is None:
            raise serializers.ValidationError("Invitation not found.")

        InvitationService._expire_invitation_if_needed(invitation)

        with transaction.atomic():
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
            ActivityLogService.log_activity(
                workspace=invitation.workspace,
                actor=requester,
                action=ActivityAction.INVITATION_REVOKED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} revoked "
                    f"{invitation.email}'s invitation."
                ),
                entity_type="workspace_invitation",
                entity_id=invitation.id,
                metadata={"email": invitation.email, "role": invitation.role},
            )
            return invitation
    
    
