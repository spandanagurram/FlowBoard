from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import WorkspaceCreateSerializer, WorkspaceSerializer
from .services import WorkspaceService


class WorkspaceCreateAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkspaceCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = WorkspaceService.create_workspace(
            owner=request.user,
            validated_data=serializer.validated_data,
        )
        response_serializer = WorkspaceSerializer(workspace)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
