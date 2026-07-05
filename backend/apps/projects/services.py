from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework import serializers

from apps.workspaces.models import Role, Workspace, WorkspaceMember

from .models import Project


class ProjectService:
    PROJECT_ORDERING_FIELDS = {"created_at", "updated_at", "name", "key"}

    @staticmethod
    def _get_active_membership(workspace, requester):
        return WorkspaceMember.objects.filter(
            workspace=workspace,
            user=requester,
            is_active=True,
        ).first()

    @staticmethod
    def create_project(requester, workspace_id, validated_data):
        with transaction.atomic():
            workspace = Workspace.objects.filter(id=workspace_id).first()
            if workspace is None:
                raise serializers.ValidationError("Workspace not found.")

            # Confirm the requester can create projects in this workspace.
            requester_membership = WorkspaceMember.objects.filter(
                workspace=workspace,
                user=requester,
                is_active=True,
            ).first()
            if requester_membership is None:
                raise serializers.ValidationError(
                    "You are not a member of this workspace."
                )

            if requester_membership.role not in {Role.OWNER, Role.ADMIN}:
                raise serializers.ValidationError(
                    "You do not have permission to create projects."
                )

            name = validated_data["name"].strip()
            key = validated_data["key"].strip().upper()

            if Project.objects.filter(
                workspace=workspace,
                name__iexact=name,
                is_deleted=False,
            ).exists():
                raise serializers.ValidationError(
                    {"name": "Project name already exists in this workspace."}
                )

            if Project.objects.filter(workspace=workspace, key=key).exists():
                raise serializers.ValidationError(
                    {"key": "Project key already exists in this workspace."}
                )

            try:
                return Project.objects.create(
                    workspace=workspace,
                    name=name,
                    key=key,
                    description=validated_data.get("description", ""),
                    created_by=requester,
                    updated_by=requester,
                )
            except IntegrityError as exc:
                raise serializers.ValidationError(
                    "Project could not be created with the provided data."
                ) from exc

    @staticmethod
    def list_projects(requester, workspace_id, search=None, ordering=None):
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if workspace is None:
            raise NotFound("Workspace not found.")

        # Only active workspace members can read projects in this workspace.
        requester_membership = ProjectService._get_active_membership(
            workspace=workspace,
            requester=requester,
        )
        if requester_membership is None:
            raise serializers.ValidationError(
                "You are not a member of this workspace."
            )

        projects = Project.objects.filter(
            workspace=workspace,
            is_deleted=False,
        )

        if search:
            projects = projects.filter(name__icontains=search.strip())

        ordering_fields = ProjectService._get_ordering_fields(ordering)
        return projects.order_by(*ordering_fields)

    @staticmethod
    def get_project_detail(requester, project_id):
        project = Project.objects.select_related("workspace").filter(
            id=project_id,
            is_deleted=False,
        ).first()
        if project is None:
            raise NotFound("Project not found.")

        # Project detail is visible to any active member of the owning workspace.
        requester_membership = ProjectService._get_active_membership(
            workspace=project.workspace,
            requester=requester,
        )
        if requester_membership is None:
            raise serializers.ValidationError(
                "You are not a member of this workspace."
            )

        return project

    @staticmethod
    def update_project(requester, project_id, validated_data):
        with transaction.atomic():
            project = Project.objects.select_related("workspace").filter(
                id=project_id,
                is_deleted=False,
            ).first()
            if project is None:
                raise NotFound("Project not found.")

            requester_membership = ProjectService._get_active_membership(
                workspace=project.workspace,
                requester=requester,
            )
            if requester_membership is None:
                raise serializers.ValidationError(
                    "You are not a member of this workspace."
                )

            if requester_membership.role not in {Role.OWNER, Role.ADMIN}:
                raise serializers.ValidationError(
                    "You do not have permission to update projects."
                )

            update_fields = ["updated_by", "updated_at"]
            if "name" in validated_data:
                name = validated_data["name"].strip()
                if Project.objects.filter(
                    workspace=project.workspace,
                    name__iexact=name,
                    is_deleted=False,
                ).exclude(id=project.id).exists():
                    raise serializers.ValidationError(
                        {"name": "Project name already exists in this workspace."}
                    )
                project.name = name
                update_fields.append("name")

            if "description" in validated_data:
                project.description = validated_data["description"]
                update_fields.append("description")

            project.updated_by = requester
            project.save(update_fields=update_fields)
            return project

    @staticmethod
    def soft_delete_project(requester, project_id):
        with transaction.atomic():
            project = Project.objects.select_related("workspace").filter(
                id=project_id,
                is_deleted=False,
            ).first()
            if project is None:
                raise NotFound("Project not found.")

            requester_membership = ProjectService._get_active_membership(
                workspace=project.workspace,
                requester=requester,
            )
            if requester_membership is None:
                raise serializers.ValidationError(
                    "You are not a member of this workspace."
                )

            if requester_membership.role != Role.OWNER:
                raise serializers.ValidationError(
                    "You do not have permission to delete projects."
                )

            # Soft-delete the project so historical references can remain intact.
            project.is_deleted = True
            project.deleted_at = timezone.now()
            project.deleted_by = requester
            project.updated_by = requester
            project.save(
                update_fields=[
                    "is_deleted",
                    "deleted_at",
                    "deleted_by",
                    "updated_by",
                    "updated_at",
                ]
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
            if field_name not in ProjectService.PROJECT_ORDERING_FIELDS:
                raise serializers.ValidationError(
                    {"ordering": "Invalid project ordering field."}
                )
            ordering_fields.append(field)

        return ordering_fields or ["-created_at"]
