from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from apps.common.models import BaseModel
from apps.workspaces.models import Workspace


class Project(BaseModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=5)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_projects",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="updated_projects",
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="deleted_projects",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "workspace",
                Lower("name"),
                condition=Q(is_deleted=False),
                name="unique_active_project_name_per_workspace",
            ),
            models.UniqueConstraint(
                fields=["workspace", "key"],
                name="unique_project_key_per_workspace",
            ),
        ]
        indexes = [
            models.Index(fields=["workspace", "is_deleted"]),
            models.Index(fields=["workspace", "key"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.key})"
