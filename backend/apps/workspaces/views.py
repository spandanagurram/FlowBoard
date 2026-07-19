from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    InvitationDetailSerializer,
    WorkspaceCreateSerializer,
    WorkspaceInvitationCreateSerializer,
    WorkspaceInvitationSerializer,
    WorkspaceMemberDetailSerializer,
    WorkspaceMemberRoleUpdateSerializer,
    WorkspaceMemberSerializer,
    WorkspaceSerializer,
    WorkspaceTransferOwnershipSerializer,
    WorkspaceUpdateSerializer,
)
from .services import InvitationService, WorkspaceService


class WorkspaceCollectionAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkspaceCreateSerializer

    def get(self, request):
        workspaces = WorkspaceService.list_workspaces(
            requester=request.user,
            search=request.query_params.get("search"),
            ordering=request.query_params.get("ordering"),
        )
        page = self.paginate_queryset(workspaces)
        if page is not None:
            serializer = WorkspaceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = WorkspaceService.create_workspace(
            owner=request.user,
            validated_data=serializer.validated_data,
        )
        response_serializer = WorkspaceSerializer(workspace)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class WorkspaceDetailAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkspaceSerializer

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return WorkspaceUpdateSerializer
        return self.serializer_class

    def get(self, request, workspace_id):
        workspace = WorkspaceService.get_workspace_detail(
            requester=request.user,
            workspace_id=workspace_id,
        )
        serializer = self.get_serializer(workspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, workspace_id):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data:
            raise serializers.ValidationError(
                "No fields provided for update."
            )

        workspace = WorkspaceService.update_workspace(
            requester=request.user,
            workspace_id=workspace_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = WorkspaceSerializer(workspace)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, workspace_id):
        WorkspaceService.soft_delete_workspace(
            requester=request.user,
            workspace_id=workspace_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkspaceTransferOwnershipAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkspaceTransferOwnershipSerializer

    def patch(self, request, workspace_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = WorkspaceService.transfer_ownership(
            requester=request.user,
            workspace_id=workspace_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = WorkspaceSerializer(workspace)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class WorkspaceMemberRoleUpdateAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkspaceMemberRoleUpdateSerializer

    def patch(self, request, workspace_id, user_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership = WorkspaceService.change_member_role(
            requester=request.user,
            workspace_id=workspace_id,
            user_id=user_id,
            validated_data=serializer.validated_data,
        )
        response_serializer = WorkspaceMemberDetailSerializer(membership)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class WorkspaceMemberRemoveAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, workspace_id, member_id):
        WorkspaceService.remove_member(
            requester=request.user,
            workspace_id=workspace_id,
            member_id=member_id,
        )
        return Response(
            {"message": "Member removed successfully."},
            status=status.HTTP_200_OK,
        )


class WorkspaceMemberListAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkspaceMemberSerializer

    def get(self, request, workspace_id):
        requester_membership, members = WorkspaceService.list_members(
            request.user,
            workspace_id,
        )

        serializer = WorkspaceMemberSerializer(members, many=True,)
        return Response({
        "current_user_role": requester_membership.role,
        "members": serializer.data,
        }, status=status.HTTP_200_OK)


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

class InvitationDetailAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = InvitationDetailSerializer

    def get(self, request, token):
        invitation = InvitationService.get_invitation(token=token)
        response_serializer = InvitationDetailSerializer(invitation)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

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
