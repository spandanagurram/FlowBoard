from django.urls import path

from .views import CreateProjectAPIView, ProjectDetailAPIView


urlpatterns = [
    path("", CreateProjectAPIView.as_view(), name="project-create"),
]

project_urlpatterns = [
    path("<uuid:project_id>/", ProjectDetailAPIView.as_view(), name="project-detail"),
]
