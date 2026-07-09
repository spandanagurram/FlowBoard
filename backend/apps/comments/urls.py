from django.urls import path

from .views import CommentCollectionAPIView, CommentDetailAPIView


urlpatterns = [
    path("", CommentCollectionAPIView.as_view(), name="comment-list-create"),
]

comment_urlpatterns = [
    path("<uuid:comment_id>/", CommentDetailAPIView.as_view(), name="comment-detail"),
]
