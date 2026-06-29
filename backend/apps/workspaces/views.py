from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    WorkspaceCreateSerializer,
    WorkspaceInvitationCreateSerializer,
    WorkspaceInvitationSerializer,
    WorkspaceSerializer,
)
from .services import InvitationService, WorkspaceService


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


class WorkspaceInvitationCreateAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkspaceInvitationCreateSerializer

    def post(self, request, workspace_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = InvitationService.create_invitation(
            requester=request.user,
            workspace_id=workspace_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = WorkspaceInvitationSerializer(invitation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class InvitationAcceptAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, token):
        invitation = InvitationService.accept_invitation(
            token=token,
            user=request.user,
        )
        response_serializer = WorkspaceInvitationSerializer(invitation)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class InvitationRejectAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, token):
        invitation = InvitationService.reject_invitation(
            token=token,
            user=request.user,
        )
        response_serializer = WorkspaceInvitationSerializer(invitation)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class InvitationRevokeAPIView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, invitation_id):
        invitation = InvitationService.revoke_invitation(
            invitation_id=invitation_id,
            requester=request.user,
        )
        response_serializer = WorkspaceInvitationSerializer(invitation)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
