from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.tasks.models import Task
from apps.workspaces.models import Role, WorkspaceMember
from apps.activities.models import ActivityAction
from apps.activities.services import ActivityLogService

from .models import Comment


class CommentService:
    @staticmethod
    def _get_active_membership(workspace, requester):
        return WorkspaceMember.objects.filter(
            workspace=workspace,
            user=requester,
            is_active=True,
        ).first()

    @staticmethod
    def _ensure_workspace_member(workspace, requester):
        membership = CommentService._get_active_membership(
            workspace=workspace,
            requester=requester,
        )
        if membership is None:
            raise serializers.ValidationError(
                "You are not a member of this workspace."
            )
        return membership

    @staticmethod
    def _get_active_task(task_id, lock=False):
        tasks = Task.objects.select_related(
            "project",
            "project__workspace",
        ).filter(
            id=task_id,
            is_deleted=False,
        )
        if lock:
            tasks = tasks.select_for_update()

        task = tasks.first()
        if task is None:
            raise NotFound("Task not found.")
        return task

    @staticmethod
    def _get_active_comment(comment_id, lock=False):
        comments = Comment.objects.select_related(
            "task",
            "task__project",
            "task__project__workspace",
            "created_by",
            "updated_by",
        ).filter(
            id=comment_id,
            is_deleted=False,
        )
        if lock:
            comments = comments.select_for_update()

        comment = comments.first()
        if comment is None:
            raise NotFound("Comment not found.")
        if comment.task.is_deleted:
            raise NotFound("Task not found.")
        return comment

    @staticmethod
    def _ensure_can_create_comment(membership):
        if membership.role == Role.VIEWER:
            raise serializers.ValidationError(
                "You do not have permission to create comments."
            )

    @staticmethod
    def _ensure_can_update_comment(comment, requester, membership):
        if membership.role == Role.VIEWER:
            raise serializers.ValidationError(
                "You do not have permission to update this comment."
            )

        if comment.created_by_id != requester.id:
            raise serializers.ValidationError(
                "You do not have permission to update this comment."
            )

    @staticmethod
    def _ensure_can_delete_comment(comment, requester, membership):
        if membership.role == Role.VIEWER:
            raise serializers.ValidationError(
                "You do not have permission to delete this comment."
            )

        if comment.created_by_id == requester.id:
            return

        if membership.role in {Role.OWNER, Role.ADMIN}:
            return

        raise serializers.ValidationError(
            "You do not have permission to delete this comment."
        )

    @staticmethod
    def create_comment(requester, task_id, validated_data):
        with transaction.atomic():
            task = CommentService._get_active_task(task_id=task_id, lock=True)
            membership = CommentService._ensure_workspace_member(
                workspace=task.project.workspace,
                requester=requester,
            )
            CommentService._ensure_can_create_comment(membership=membership)

            comment = Comment.objects.create(
                task=task,
                content=validated_data["content"],
                created_by=requester,
                updated_by=requester,
            )
            ActivityLogService.log_activity(
                workspace=task.project.workspace,
                actor=requester,
                action=ActivityAction.COMMENT_CREATED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} created a comment."
                ),
                entity_type="comment",
                entity_id=comment.id,
            )
            return comment

    @staticmethod
    def list_comments(requester, task_id, search=None):
        task = CommentService._get_active_task(task_id=task_id)
        CommentService._ensure_workspace_member(
            workspace=task.project.workspace,
            requester=requester,
        )

        comments = Comment.objects.select_related(
            "task",
            "created_by",
            "updated_by",
        ).filter(
            task=task,
            is_deleted=False,
        )

        if search:
            search = search.strip()
            if search:
                comments = comments.filter(content__icontains=search)

        return comments.order_by("created_at")

    @staticmethod
    def update_comment(requester, comment_id, validated_data):
        with transaction.atomic():
            comment = CommentService._get_active_comment(
                comment_id=comment_id,
                lock=True,
            )
            membership = CommentService._ensure_workspace_member(
                workspace=comment.task.project.workspace,
                requester=requester,
            )
            CommentService._ensure_can_update_comment(
                comment=comment,
                requester=requester,
                membership=membership,
            )

            comment.content = validated_data["content"]
            comment.edited_at = timezone.now()
            comment.updated_by = requester
            comment.save(
                update_fields=["content", "edited_at", "updated_by", "updated_at"]
            )
            ActivityLogService.log_activity(
                workspace=comment.task.project.workspace,
                actor=requester,
                action=ActivityAction.COMMENT_UPDATED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} edited a comment."
                ),
                entity_type="comment",
                entity_id=comment.id,
            )
            return comment

    @staticmethod
    def delete_comment(requester, comment_id):
        with transaction.atomic():
            comment = CommentService._get_active_comment(
                comment_id=comment_id,
                lock=True,
            )
            membership = CommentService._ensure_workspace_member(
                workspace=comment.task.project.workspace,
                requester=requester,
            )
            CommentService._ensure_can_delete_comment(
                comment=comment,
                requester=requester,
                membership=membership,
            )

            comment.is_deleted = True
            comment.deleted_at = timezone.now()
            comment.deleted_by = requester
            comment.updated_by = requester
            comment.save(
                update_fields=[
                    "is_deleted",
                    "deleted_at",
                    "deleted_by",
                    "updated_by",
                    "updated_at",
                ]
            )
            ActivityLogService.log_activity(
                workspace=comment.task.project.workspace,
                actor=requester,
                action=ActivityAction.COMMENT_DELETED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} deleted a comment."
                ),
                entity_type="comment",
                entity_id=comment.id,
            )
