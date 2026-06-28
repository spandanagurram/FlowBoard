from django.urls import path

from .views import WorkspaceCreateAPIView


urlpatterns = [
    path("", WorkspaceCreateAPIView.as_view(), name="workspace-create"),
]
