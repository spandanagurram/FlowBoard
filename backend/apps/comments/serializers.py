from rest_framework import serializers

from .models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)

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

    def validate_content(self, value):
        content = value.strip()
        if not content:
            raise serializers.ValidationError("Comment content cannot be empty.")
        if len(content) > 5000:
            raise serializers.ValidationError(
                "Comment content cannot exceed 5000 characters."
            )
        return content


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)

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

    def validate_content(self, value):
        content = value.strip()
        if not content:
            raise serializers.ValidationError("Comment content cannot be empty.")
        if len(content) > 5000:
            raise serializers.ValidationError(
                "Comment content cannot exceed 5000 characters."
            )
        return content


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "task",
            "content",
            "created_by",
            "updated_by",
            "edited_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
