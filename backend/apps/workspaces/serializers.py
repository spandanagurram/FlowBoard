from rest_framework import serializers

from .models import InvitationRole, Workspace, WorkspaceInvitation


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("name", "description", "logo")

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Workspace name cannot be empty.")

        request = self.context.get("request")
        owner = getattr(request, "user", None)
        if owner and Workspace.objects.filter(owner=owner, name__iexact=name).exists():
            raise serializers.ValidationError(
                "You already have a workspace with this name."
            )

        return name


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = (
            "id",
            "name",
            "description",
            "logo",
            "owner",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class WorkspaceInvitationCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=InvitationRole.choices)


class WorkspaceInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceInvitation
        fields = (
            "id",
            "workspace",
            "email",
            "role",
            "status",
            "expires_at",
            "accepted_at",
            "invited_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
