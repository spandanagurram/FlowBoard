from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
)
from .services import CommentService


class CommentCollectionAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentCreateSerializer

    def get(self, request, task_id):
        comments = CommentService.list_comments(
            requester=request.user,
            task_id=task_id,
            search=request.query_params.get("search"),
        )
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = CommentService.create_comment(
            requester=request.user,
            task_id=task_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentUpdateSerializer

    def patch(self, request, comment_id):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data:
            raise serializers.ValidationError("No fields provided for update.")

        comment = CommentService.update_comment(
            requester=request.user,
            comment_id=comment_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, comment_id):
        CommentService.delete_comment(
            requester=request.user,
            comment_id=comment_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
