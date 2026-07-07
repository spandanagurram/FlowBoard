from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.projects.models import Project
from apps.workspaces.models import Role, WorkspaceMember

from .models import Priority, Task, TaskStatus


User = get_user_model()


class TaskService:
    TASK_ORDERING_FIELDS = {
        "created_at",
        "updated_at",
        "task_number",
        "title",
        "status",
        "priority",
        "due_date",
    }

    @staticmethod
    def _get_active_membership(workspace, requester):
        return WorkspaceMember.objects.filter(
            workspace=workspace,
            user=requester,
            is_active=True,
        ).first()

    @staticmethod
    def _get_active_project(project_id, lock=False):
        projects = Project.objects.select_related("workspace").filter(
            id=project_id,
            is_deleted=False,
        )
        if lock:
            projects = projects.select_for_update()
        project = projects.first()
        if project is None:
            raise NotFound("Project not found.")
        return project

    @staticmethod
    def _ensure_workspace_member(workspace, requester):
        membership = TaskService._get_active_membership(
            workspace=workspace,
            requester=requester,
        )
        if membership is None:
            raise serializers.ValidationError(
                "You are not a member of this workspace."
            )
        return membership

    @staticmethod
    def _get_assignee(project, assignee_id):
        if assignee_id is None:
            return None

        assignee = User.objects.filter(id=assignee_id).first()
        if assignee is None:
            raise serializers.ValidationError({"assignee": "Assignee not found."})

        assignee_membership = WorkspaceMember.objects.filter(
            workspace=project.workspace,
            user=assignee,
            is_active=True,
        ).first()
        
        if assignee_membership is None:
            raise serializers.ValidationError(
                {"assignee": "Assignee must be an active member of this workspace."}
            )

        if assignee_membership.role == Role.VIEWER:
            raise serializers.ValidationError(
                {"assignee": "Viewer cannot be assigned tasks."}
            )
        return assignee

    @staticmethod
    def _get_parent_task(project, parent_task_id):
        if parent_task_id is None:
            return None

        parent = Task.objects.filter(
            id=parent_task_id,
            is_deleted=False,
        ).first()
        if parent is None:
            raise serializers.ValidationError({"parent_task": "Parent task not found."})

        if parent.project_id != project.id:
            raise serializers.ValidationError(
                {"parent_task": "Parent task must belong to the same project."}
            )

        if parent.parent_task_id is not None:
            raise serializers.ValidationError(
                {"parent_task": "A subtask cannot have another subtask."}
            )

        return parent

    @staticmethod
    def create_task(requester, project_id, validated_data):
        with transaction.atomic():
            # Lock the project row so task numbers remain sequential per project.
            project = TaskService._get_active_project(project_id=project_id, lock=True)
            requester_membership = TaskService._ensure_workspace_member(
                workspace=project.workspace,
                requester=requester,
            )
            if requester_membership.role not in {Role.OWNER, Role.ADMIN}:
                raise serializers.ValidationError(
                    "You do not have permission to create tasks."
                )

            parent_task = TaskService._get_parent_task(
                project=project,
                parent_task_id=validated_data.get("parent_task"),
            )
            title = validated_data["title"]
            if parent_task is None:
                if Task.objects.filter(
                    project=project,
                    parent_task__isnull=True,
                    title__iexact=title,
                    is_deleted=False,
                ).exists():
                    raise serializers.ValidationError(
                        {
                            "title": "Task title already exists in this project."
                        }
                    )
            else:
                if Task.objects.filter(
                    project=project,
                    parent_task=parent_task,
                    title__iexact=title,
                    is_deleted=False,
                ).exists():
                    raise serializers.ValidationError(
                        {
                            "title": "Subtask title already exists under this parent task."
                        }
                    )
            assignee = TaskService._get_assignee(
                project=project,
                assignee_id=validated_data.get("assignee"),
            )
            task_number = TaskService._generate_task_number(
                project=project,
                parent_task=parent_task,
            )
            try:
                return Task.objects.create(
                    project=project,
                    parent_task=parent_task,
                    task_number=task_number,
                    title=validated_data["title"],
                    description=validated_data.get("description", ""),
                    status=validated_data.get("status", TaskStatus.TODO),
                    priority=validated_data.get("priority", Priority.MEDIUM),
                    assignee=assignee,
                    due_date=validated_data.get("due_date"),
                    created_by=requester,
                    updated_by=requester,
                )
            except IntegrityError as exc:
                raise serializers.ValidationError(
                    "Task could not be created with the provided data."
                ) from exc

    @staticmethod
    def list_tasks(requester, project_id, search=None, ordering=None):
        project = TaskService._get_active_project(project_id=project_id)
        TaskService._ensure_workspace_member(
            workspace=project.workspace,
            requester=requester,
        )

        tasks = Task.objects.filter(
            project=project,
            is_deleted=False,
        )

        if search:
            tasks = tasks.filter(title__icontains=search.strip())

        ordering_fields = TaskService._get_ordering_fields(ordering)
        return tasks.order_by(*ordering_fields)

    @staticmethod
    def get_task_detail(requester, task_id):
        task = Task.objects.select_related("project", "project__workspace").filter(
            id=task_id,
            is_deleted=False,
        ).first()
        if task is None:
            raise NotFound("Task not found.")

        TaskService._ensure_workspace_member(
            workspace=task.project.workspace,
            requester=requester,
        )
        return task

    @staticmethod
    def _generate_task_number(project, parent_task=None):
        if parent_task is None:
            sibling_numbers = Task.objects.filter(
                project=project,
                parent_task__isnull=True,
            ).values_list("task_number", flat=True)
            prefix = project.key
        else:
            sibling_numbers = Task.objects.filter(
                project=project,
                parent_task=parent_task,
            ).values_list("task_number", flat=True)
            prefix = parent_task.task_number

        next_number = TaskService._get_next_sequence_number(
            prefix=prefix,
            task_numbers=sibling_numbers,
        )
        return f"{prefix}-{next_number}"

    @staticmethod
    def _get_next_sequence_number(prefix, task_numbers):
        max_number = 0
        prefix = f"{prefix}-"

        for task_number in task_numbers:
            if not task_number.startswith(prefix):
                continue

            suffix = task_number.removeprefix(prefix)
            if suffix.isdigit():
                max_number = max(max_number, int(suffix))

        return max_number + 1

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
            if field_name not in TaskService.TASK_ORDERING_FIELDS:
                raise serializers.ValidationError(
                    {"ordering": "Invalid task ordering field."}
                )
            ordering_fields.append(field)

        return ordering_fields or ["-created_at"]
