from django.conf import settings
from django.db import models

from apps.common.models import BaseModel
from apps.tasks.models import Task


class Comment(BaseModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_comments",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="updated_comments",
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="deleted_comments",
        null=True,
        blank=True,
    )
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["task", "is_deleted", "created_at"]),
            models.Index(fields=["created_by", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.task.task_number} comment by {self.created_by.email}"
