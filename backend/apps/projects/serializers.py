from rest_framework import serializers

from .models import Project


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("name", "key", "description")

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Project name cannot be empty.")
        return name

    def validate_key(self, value):
        key = value.strip().upper()
        if not 2 <= len(key) <= 5:
            raise serializers.ValidationError(
                "Project key must be between 2 and 5 characters."
            )
        return key


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
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
            raise serializers.ValidationError("Project name cannot be empty.")
        return name


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "workspace",
            "name",
            "key",
            "description",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
