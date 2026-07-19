from django.urls import include, path

from .views import (
    InvitationDetailAPIView,
    InvitationAcceptAPIView,
    InvitationRejectAPIView,
    InvitationRevokeAPIView,
    WorkspaceCollectionAPIView,
    WorkspaceDetailAPIView,
    WorkspaceInvitationCreateAPIView,
    WorkspaceMemberListAPIView,
    WorkspaceMemberRemoveAPIView,
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
        "<uuid:workspace_id>/members/",
        WorkspaceMemberListAPIView.as_view(),
        name="workspace-member-list",
    ),
    path(
        "<uuid:workspace_id>/members/<uuid:user_id>/role/",
        WorkspaceMemberRoleUpdateAPIView.as_view(),
        name="workspace-member-role-update",
    ),
    path(
        "<uuid:workspace_id>/members/<uuid:member_id>/",
        WorkspaceMemberRemoveAPIView.as_view(),
        name="workspace-member-remove",
    ),
    path(
        "<uuid:workspace_id>/projects/",
        include("apps.projects.urls"),
    ),
    path(
        "<uuid:workspace_id>/activities/",
        include("apps.activities.urls"),
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
    path(
        "<str:token>/",
        InvitationDetailAPIView.as_view(),
        name="workspace-invitation-detail",
    ),
]
