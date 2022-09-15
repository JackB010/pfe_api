from django.urls import path
from rest_framework import routers

from .views import (
    CommentLikersAPI,
    FavoritePostAPI,
    FollowingPostsAPI,
    LikePostAPI,
    LikePostCommentAPI,
    PostCommentAPI,
    PostCommentUpdateAPI,
    PostLikersAPI,
    PostViewSet,
    SavePostAPI,
    SearchPost,
)

router = routers.DefaultRouter()
router.register(r"", PostViewSet)
# router.register(r"comment", PostCommentViewSet)

urlpatterns = [
    path(
        "comment/update/<str:cid>/",
        PostCommentUpdateAPI.as_view(),
        name="comment_update",
    ),
    path(
        "comment/likers/<str:cid>/", CommentLikersAPI.as_view(), name="comment_likers"
    ),
    path("comment/like/", LikePostCommentAPI.as_view(), name="comment_like"),
    path("comment/<str:pid>/", PostCommentAPI.as_view(), name="comment"),
    path("like/", LikePostAPI.as_view(), name="like_post"),
    path("favorite/", FavoritePostAPI.as_view(), name="like_post"),
    path("save/", SavePostAPI.as_view(), name="like_post"),
    path("following/", FollowingPostsAPI.as_view(), name="following_posts"),
    path("search/", SearchPost.as_view(), name="search_post"),
    path("likers/<str:pid>/", PostLikersAPI.as_view(), name="post_likers"),
]
urlpatterns += router.urls
