from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import TaskCreateSerializer, TaskSerializer
from .services import TaskService


class TaskCollectionAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskCreateSerializer

    def get(self, request, project_id):
        tasks = TaskService.list_tasks(
            requester=request.user,
            project_id=project_id,
            search=request.query_params.get("search"),
            ordering=request.query_params.get("ordering"),
        )
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = TaskService.create_task(
            requester=request.user,
            project_id=project_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = TaskSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get(self, request, task_id):
        task = TaskService.get_task_detail(
            requester=request.user,
            task_id=task_id,
        )
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
