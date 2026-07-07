from rest_framework import serializers

from .models import Task


class TaskCreateSerializer(serializers.ModelSerializer):
    parent_task = serializers.UUIDField(required=False, allow_null=True)
    assignee = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = (
            "parent_task",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "due_date",
        )
        extra_kwargs = {
            "description": {"required": False},
            "status": {"required": False},
            "priority": {"required": False},
            "due_date": {"required": False, "allow_null": True},
        }

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

    def validate_title(self, value):
        title = value.strip()
        if not title:
            raise serializers.ValidationError("Task title cannot be empty.")
        return title


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "project",
            "parent_task",
            "task_number",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "due_date",
            "completed_at",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
