from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    workspace_count = serializers.IntegerField(read_only=True)
    project_count = serializers.IntegerField(read_only=True)
    task_count = serializers.IntegerField(read_only=True)
