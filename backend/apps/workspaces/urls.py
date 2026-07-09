from django.urls import include, path

from .views import (
    InvitationAcceptAPIView,
    InvitationRejectAPIView,
    InvitationRevokeAPIView,
    WorkspaceCollectionAPIView,
    WorkspaceDetailAPIView,
    WorkspaceInvitationCreateAPIView,
    WorkspaceMemberRoleUpdateAPIView,
    WorkspaceTransferOwnershipAPIView,
)


urlpatterns = [
    path("", WorkspaceCollectionAPIView.as_view(), name="workspace-list-create"),
    path(
        "<uuid:workspace_id>/",
        WorkspaceDetailAPIView.as_view(),
        name="workspace-detail",
    ),
    path(
        "<uuid:workspace_id>/transfer-ownership/",
        WorkspaceTransferOwnershipAPIView.as_view(),
        name="workspace-transfer-ownership",
    ),
    path(
        "<uuid:workspace_id>/invitations/",
        WorkspaceInvitationCreateAPIView.as_view(),
        name="workspace-invitation-create",
    ),
    path(
        "<uuid:workspace_id>/members/<uuid:user_id>/role/",
        WorkspaceMemberRoleUpdateAPIView.as_view(),
        name="workspace-member-role-update",
    ),
    path(
        "<uuid:workspace_id>/projects/",
        include("apps.projects.urls"),
    ),
]

invitation_urlpatterns = [
    path(
        "<str:token>/accept/",
        InvitationAcceptAPIView.as_view(),
        name="workspace-invitation-accept",
    ),
    path(
        "<str:token>/reject/",
        InvitationRejectAPIView.as_view(),
        name="workspace-invitation-reject",
    ),
    path(
        "<uuid:invitation_id>/revoke/",
        InvitationRevokeAPIView.as_view(),
        name="workspace-invitation-revoke",
    ),
]
