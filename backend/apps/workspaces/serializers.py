from rest_framework import serializers

from .models import Workspace


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
