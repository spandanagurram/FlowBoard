from django.urls import include, path

from .views import (
    InvitationAcceptAPIView,
    InvitationRejectAPIView,
    InvitationRevokeAPIView,
    WorkspaceCreateAPIView,
    WorkspaceInvitationCreateAPIView,
)


urlpatterns = [
    path("", WorkspaceCreateAPIView.as_view(), name="workspace-create"),
    path(
        "<uuid:workspace_id>/invitations/",
        WorkspaceInvitationCreateAPIView.as_view(),
        name="workspace-invitation-create",
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
