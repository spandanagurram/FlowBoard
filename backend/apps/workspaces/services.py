from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Role, Workspace, WorkspaceMember


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
