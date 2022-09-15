from django.urls import path
from rest_framework import routers

from .views import (
    CommentLikersAPI,
    FavoriteImageAPI,
    FollowingImagesAPI,
    ImageAPI,
    ImageCommentAPI,
    ImageCommentUpdateAPI,
    ImageLikersAPI,
    ImageUpdateAPI,
    LikeImageAPI,
    LikeImageCommentAPI,
    SaveImageAPI,
    SearchImage,
)

# router = routers.DefaultRouter()
# router.register(r"", ImageViewSet)

urlpatterns = [
    path("", ImageAPI.as_view(), name="images"),
    path(
        "comment/update/<str:cid>/",
        ImageCommentUpdateAPI.as_view(),
        name="comment_update",
    ),
    path(
        "comment/likers/<str:cid>/", CommentLikersAPI.as_view(), name="comment_likers"
    ),
    path("comment/like/", LikeImageCommentAPI.as_view(), name="comment_like"),
    path("comment/<str:iid>/", ImageCommentAPI.as_view(), name="comment"),
    path("like/", LikeImageAPI.as_view(), name="like_post"),
    path("favorite/", FavoriteImageAPI.as_view(), name="like_post"),
    path("save/", SaveImageAPI.as_view(), name="like_post"),
    path("following/", FollowingImagesAPI.as_view(), name="following_images"),
    path("search/", SearchImage.as_view(), name="search_images"),
    path("<str:iid>/", ImageUpdateAPI.as_view(), name="image_update"),
    path("likers/<str:iid>/", ImageLikersAPI.as_view(), name="image_likers"),
]

# urlpatterns += router.urls
