from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import BaseModel
from apps.workspaces.models import Workspace


class ActivityAction(models.TextChoices):
    WORKSPACE_CREATED = "WORKSPACE_CREATED", "Workspace created"
    WORKSPACE_UPDATED = "WORKSPACE_UPDATED", "Workspace updated"
    WORKSPACE_DELETED = "WORKSPACE_DELETED", "Workspace deleted"
    WORKSPACE_TRANSFERRED = "WORKSPACE_TRANSFERRED", "Workspace transferred"
    INVITATION_SENT = "INVITATION_SENT", "Invitation sent"
    INVITATION_ACCEPTED = "INVITATION_ACCEPTED", "Invitation accepted"
    INVITATION_REJECTED = "INVITATION_REJECTED", "Invitation rejected"
    INVITATION_REVOKED = "INVITATION_REVOKED", "Invitation revoked"
    INVITATION_EXPIRED = "INVITATION_EXPIRED", "Invitation expired"
    MEMBER_ROLE_CHANGED = "MEMBER_ROLE_CHANGED", "Member role changed"
    PROJECT_CREATED = "PROJECT_CREATED", "Project created"
    PROJECT_UPDATED = "PROJECT_UPDATED", "Project updated"
    PROJECT_DELETED = "PROJECT_DELETED", "Project deleted"
    TASK_CREATED = "TASK_CREATED", "Task created"
    TASK_UPDATED = "TASK_UPDATED", "Task updated"
    TASK_DELETED = "TASK_DELETED", "Task deleted"
    TASK_ASSIGNED = "TASK_ASSIGNED", "Task assigned"
    TASK_UNASSIGNED = "TASK_UNASSIGNED", "Task unassigned"
    TASK_STATUS_CHANGED = "TASK_STATUS_CHANGED", "Task status changed"
    TASK_PRIORITY_CHANGED = "TASK_PRIORITY_CHANGED", "Task priority changed"
    TASK_DUE_DATE_CHANGED = "TASK_DUE_DATE_CHANGED", "Task due date changed"
    COMMENT_CREATED = "COMMENT_CREATED", "Comment created"
    COMMENT_UPDATED = "COMMENT_UPDATED", "Comment updated"
    COMMENT_DELETED = "COMMENT_DELETED", "Comment deleted"


class ActivityLog(BaseModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="activity_logs",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=40, choices=ActivityAction.choices)
    description = models.TextField()
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "-created_at"]),
            models.Index(fields=["workspace", "action"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("Activity logs cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Activity logs cannot be deleted.")
