from django.urls import include, path

from .views import TaskCollectionAPIView, TaskDetailAPIView


urlpatterns = [
    path("", TaskCollectionAPIView.as_view(), name="task-create"),
]

task_urlpatterns = [
    path("<uuid:task_id>/", TaskDetailAPIView.as_view(), name="task-detail"),
    path("<uuid:task_id>/comments/", include("apps.comments.urls")),
]
