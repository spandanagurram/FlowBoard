from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    ProjectCreateSerializer,
    ProjectSerializer,
    ProjectUpdateSerializer,
)
from .services import ProjectService


class CreateProjectAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectCreateSerializer

    def get(self, request, workspace_id):
        projects = ProjectService.list_projects(
            requester=request.user,
            workspace_id=workspace_id,
            search=request.query_params.get("search"),
            ordering=request.query_params.get("ordering"),
        )
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = ProjectSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, workspace_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.create_project(
            requester=request.user,
            workspace_id=workspace_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = ProjectSerializer(project)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ProjectDetailAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ProjectUpdateSerializer
        return ProjectSerializer

    def get(self, request, project_id):
        project = ProjectService.get_project_detail(
            requester=request.user,
            project_id=project_id,
        )
        serializer = self.get_serializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, project_id):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.update_project(
            requester=request.user,
            project_id=project_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = ProjectSerializer(project)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, project_id):
        ProjectService.soft_delete_project(
            requester=request.user,
            project_id=project_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
