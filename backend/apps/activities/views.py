from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ActivityLogSerializer
from .services import ActivityLogService


class ActivityLogListAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ActivityLogSerializer

    def get(self, request, workspace_id):
        activities = ActivityLogService.list_activities(
            requester=request.user,
            workspace_id=workspace_id,
            search=request.query_params.get("search"),
        )
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
