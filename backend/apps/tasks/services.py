from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.projects.models import Project
from apps.workspaces.models import Role, WorkspaceMember
from apps.activities.models import ActivityAction
from apps.activities.services import ActivityLogService

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
    MEMBER_STATUS_TRANSITIONS = {
        TaskStatus.TODO: TaskStatus.IN_PROGRESS,
        TaskStatus.IN_PROGRESS: TaskStatus.REVIEW,
        TaskStatus.REVIEW: TaskStatus.DONE,
        TaskStatus.DONE: TaskStatus.REOPENED,
        TaskStatus.REOPENED: TaskStatus.IN_PROGRESS,
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
    def _validate_unique_title(project, title, parent_task=None, task=None):
        title_filter = {
            "project": project,
            "parent_task": parent_task,
            "title__iexact": title,
            "is_deleted": False,
        }
        duplicate_tasks = Task.objects.filter(**title_filter)
        if task is not None:
            # Updates must ignore the current row when checking sibling titles.
            duplicate_tasks = duplicate_tasks.exclude(id=task.id)

        if not duplicate_tasks.exists():
            return

        if parent_task is None:
            raise serializers.ValidationError(
                {"title": "Task title already exists in this project."}
            )

        raise serializers.ValidationError(
            {"title": "Subtask title already exists under this parent task."}
        )

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
        else:
            tasks = tasks.select_related(
                "parent_task",
                "assignee",
            )

        task = tasks.first()
        if task is None:
            raise NotFound("Task not found.")
        return task

    @staticmethod
    def _ensure_can_update_task(task, requester, membership, validated_data):
        if membership.role in {Role.OWNER, Role.ADMIN}:
            return

        if membership.role == Role.MEMBER:
            if set(validated_data.keys()) != {"status"}:
                raise serializers.ValidationError(
                    "Members may only update task status."
                )

            if task.assignee_id is None or task.assignee_id != requester.id:
                raise serializers.ValidationError(
                    "You do not have permission to update this task."
                )
            return

        raise serializers.ValidationError(
            "You do not have permission to update this task."
        )

    @staticmethod
    def _validate_member_status_transition(current_status, next_status):
        allowed_status = TaskService.MEMBER_STATUS_TRANSITIONS.get(current_status)
        if allowed_status != next_status:
            raise serializers.ValidationError(
                {"status": "Invalid task status transition."}
            )

    @staticmethod
    def _set_completed_at_for_status_change(task, next_status, update_fields):
        if next_status == TaskStatus.DONE and task.status != TaskStatus.DONE:
            task.completed_at = timezone.now()
            update_fields.add("completed_at")
        elif task.status == TaskStatus.DONE and next_status != TaskStatus.DONE:
            task.completed_at = None
            update_fields.add("completed_at")

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
            TaskService._validate_unique_title(
                project=project,
                parent_task=parent_task,
                title=title,
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
                task = Task.objects.create(
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
                ActivityLogService.log_activity(
                    workspace=project.workspace,
                    actor=requester,
                    action=ActivityAction.TASK_CREATED,
                    description=(
                        f"{ActivityLogService.get_actor_name(requester)} created "
                        f"task {task.task_number}."
                    ),
                    entity_type="task",
                    entity_id=task.id,
                )
                return task
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
        task = TaskService._get_active_task(task_id=task_id)

        TaskService._ensure_workspace_member(
            workspace=task.project.workspace,
            requester=requester,
        )
        return task

    @staticmethod
    def update_task(requester, task_id, validated_data):
        with transaction.atomic():
            task = TaskService._get_active_task(task_id=task_id, lock=True)
            requester_membership = TaskService._ensure_workspace_member(
                workspace=task.project.workspace,
                requester=requester,
            )
            TaskService._ensure_can_update_task(
                task=task,
                requester=requester,
                membership=requester_membership,
                validated_data=validated_data,
            )

            old_status = task.status
            old_priority = task.priority
            old_due_date = task.due_date
            old_assignee = task.assignee
            update_fields = set()
            if "title" in validated_data:
                TaskService._validate_unique_title(
                    project=task.project,
                    parent_task=task.parent_task,
                    title=validated_data["title"],
                    task=task,
                )
                task.title = validated_data["title"]
                update_fields.add("title")

            if "description" in validated_data:
                task.description = validated_data["description"]
                update_fields.add("description")

            if "priority" in validated_data:
                task.priority = validated_data["priority"]
                update_fields.add("priority")

            if "assignee" in validated_data:
                task.assignee = TaskService._get_assignee(
                    project=task.project,
                    assignee_id=validated_data["assignee"],
                )
                update_fields.add("assignee")

            if "due_date" in validated_data:
                task.due_date = validated_data["due_date"]
                update_fields.add("due_date")

            if "status" in validated_data:
                next_status = validated_data["status"]
                if requester_membership.role == Role.MEMBER:
                    TaskService._validate_member_status_transition(
                        current_status=task.status,
                        next_status=next_status,
                    )
                TaskService._set_completed_at_for_status_change(
                    task=task,
                    next_status=next_status,
                    update_fields=update_fields,
                )
                task.status = next_status
                update_fields.add("status")

            # Include auto_now and audit fields explicitly because save()
            # is constrained with update_fields.
            task.updated_by = requester
            update_fields.update({"updated_by", "updated_at"})
            task.save(update_fields=update_fields)

            workspace = task.project.workspace
            actor_name = ActivityLogService.get_actor_name(requester)
            
            if old_assignee != task.assignee:
                if task.assignee is None:
                    ActivityLogService.log_activity(
                        workspace=workspace,
                        actor=requester,
                        action=ActivityAction.TASK_UNASSIGNED,
                        description=f"{actor_name} unassigned task {task.task_number}.",
                        entity_type="task",
                        entity_id=task.id,
                        metadata={
                            "old_assignee": ActivityLogService.get_actor_name(old_assignee),
                            "new_assignee": None,
                        },
                    )
                else:
                    ActivityLogService.log_activity(
                        workspace=workspace,
                        actor=requester,
                        action=ActivityAction.TASK_ASSIGNED,
                        description=(
                            f"{actor_name} assigned task {task.task_number} to "
                            f"{ActivityLogService.get_actor_name(task.assignee)}."
                        ),
                        entity_type="task",
                        entity_id=task.id,
                        metadata={
                            "old_assignee": (
                                ActivityLogService.get_actor_name(old_assignee)
                                if old_assignee else None
                            ),
                            "new_assignee": ActivityLogService.get_actor_name(task.assignee),
                        },
                    )
            if old_status != task.status:
                ActivityLogService.log_activity(
                    workspace=workspace,
                    actor=requester,
                    action=ActivityAction.TASK_STATUS_CHANGED,
                    description=(
                        f"{actor_name} changed task {task.task_number} status from "
                        f"{old_status} to {task.status}."
                    ),
                    entity_type="task",
                    entity_id=task.id,
                    metadata={"old_status": old_status, "new_status": task.status},
                )
            if old_priority != task.priority:
                ActivityLogService.log_activity(
                    workspace=workspace,
                    actor=requester,
                    action=ActivityAction.TASK_PRIORITY_CHANGED,
                    description=(
                        f"{actor_name} changed task {task.task_number} priority from "
                        f"{old_priority} to {task.priority}."
                    ),
                    entity_type="task",
                    entity_id=task.id,
                    metadata={"old_priority": old_priority, "new_priority": task.priority},
                )
            if old_due_date != task.due_date:
                ActivityLogService.log_activity(
                    workspace=workspace,
                    actor=requester,
                    action=ActivityAction.TASK_DUE_DATE_CHANGED,
                    description=f"{actor_name} changed due date for task {task.task_number}.",
                    entity_type="task",
                    entity_id=task.id,
                    metadata={
                        "old_due_date": old_due_date.isoformat() if old_due_date else None,
                        "new_due_date": task.due_date.isoformat() if task.due_date else None,
                    },
                )

        return task

    @staticmethod
    def delete_task(requester, task_id):
        with transaction.atomic():
            task = TaskService._get_active_task(task_id=task_id, lock=True)
            requester_membership = TaskService._ensure_workspace_member(
                workspace=task.project.workspace,
                requester=requester,
            )
            if requester_membership.role != Role.OWNER:
                raise serializers.ValidationError(
                    "You do not have permission to delete this task."
                )

            task.is_deleted = True
            task.deleted_at = timezone.now()
            task.deleted_by = requester
            task.updated_by = requester
            task.save(
                update_fields={
                    "is_deleted",
                    "deleted_at",
                    "deleted_by",
                    "updated_by",
                    "updated_at",
                }
            )
            ActivityLogService.log_activity(
                workspace=task.project.workspace,
                actor=requester,
                action=ActivityAction.TASK_DELETED,
                description=(
                    f"{ActivityLogService.get_actor_name(requester)} deleted "
                    f"task {task.task_number}."
                ),
                entity_type="task",
                entity_id=task.id,
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
