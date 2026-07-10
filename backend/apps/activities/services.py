from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.workspaces.models import Workspace, WorkspaceMember

from .models import ActivityLog


class ActivityLogService:
    @staticmethod
    def get_actor_name(actor):
        if actor is None:
            return "System"
        return actor.get_full_name() or actor.username or actor.email

    @staticmethod
    def get_role_label(role):
        return role.replace("_", " ").title()

    @staticmethod
    def log_activity(
        workspace,
        actor,
        action,
        description,
        entity_type,
        entity_id,
        metadata=None,
    ):
        return ActivityLog.objects.create(
            workspace=workspace,
            actor=actor,
            action=action,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
        )

    @staticmethod
    def list_activities(requester, workspace_id, search=None):
        workspace = Workspace.objects.filter(
            id=workspace_id
        ).first()
        if workspace is None:
            raise NotFound("Workspace not found.")

        is_active_member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=requester,
            is_active=True,
        ).exists()
        if not is_active_member:
            raise serializers.ValidationError(
                "You are not a member of this workspace."
            )

        activities = ActivityLog.objects.select_related("actor").filter(
            workspace=workspace,
        )
        if search:
            search = search.strip()
            if search:
                activities = activities.filter(description__icontains=search)

        return activities.order_by("-created_at")
