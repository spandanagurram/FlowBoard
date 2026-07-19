from rest_framework import serializers

from .models import InvitationRole, Role, Workspace, WorkspaceInvitation, WorkspaceMember


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("name", "description", "logo")

    def validate(self, attrs):
        allowed_fields = set(self.fields.keys())
        invalid_fields = set(self.initial_data.keys()) - allowed_fields
        if invalid_fields:
            raise serializers.ValidationError(
                {
                    field: "This field cannot be set."
                    for field in sorted(invalid_fields)
                }
            )
        return attrs

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Workspace name cannot be empty.")

        if Workspace.objects.filter(
            name__iexact=name,
            is_deleted=False,
        ).exists():
            raise serializers.ValidationError(
                "Workspace name already exists."
            )

        return name


class WorkspaceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("name", "description")

    def validate(self, attrs):
        allowed_fields = set(self.fields.keys())
        invalid_fields = set(self.initial_data.keys()) - allowed_fields
        if invalid_fields:
            raise serializers.ValidationError(
                {
                    field: "This field cannot be updated."
                    for field in sorted(invalid_fields)
                }
            )
        return attrs

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Workspace name cannot be empty.")
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


class WorkspaceTransferOwnershipSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

    def validate(self, attrs):
        allowed_fields = set(self.fields.keys())
        invalid_fields = set(self.initial_data.keys()) - allowed_fields
        if invalid_fields:
            raise serializers.ValidationError(
                {
                    field: "This field cannot be set."
                    for field in sorted(invalid_fields)
                }
            )
        return attrs


class WorkspaceMemberRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=(Role.ADMIN, Role.MEMBER, Role.VIEWER))

    def validate(self, attrs):
        allowed_fields = set(self.fields.keys())
        invalid_fields = set(self.initial_data.keys()) - allowed_fields
        if invalid_fields:
            raise serializers.ValidationError(
                {
                    field: "This field cannot be updated."
                    for field in sorted(invalid_fields)
                }
            )
        return attrs


class WorkspaceMemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMember
        fields = (
            "id",
            "workspace",
            "user",
            "role",
            "invited_by",
            "joined_at",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ("id", "user_id","username", "email", "role")
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
        
        
class InvitationDetailSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)

    class Meta:
        model = WorkspaceInvitation
        fields = (
            "workspace_name",
            "email",
            "role",
            "status",
            "expires_at",
        )
