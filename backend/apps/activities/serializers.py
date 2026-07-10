from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = (
            "id",
            "workspace",
            "actor",
            "action",
            "description",
            "entity_type",
            "entity_id",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
