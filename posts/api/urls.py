from django.urls import path
from rest_framework import routers

from .views import (
    CommentLikersAPI,
    FavoritePostAPI,
    FavoritedSavedPostsAPI,
    LikePostAPI,
    LikePostCommentAPI,
    PostCommentAPI,
    PostCommentUpdateAPI,
    PostLikersAPI,
    PostViewSet,
    SavePostAPI,
    SearchPost,
    ReplyCommentAPI,
    ReplyCommentLikersAPI,
    ReplyCommentUpdateAPI,
    LikeCommentReplyAPI,
    ImageItemAPI,
    SearchPostInUser,
    SearchPostInTag,
    clear_images,
)

router = routers.DefaultRouter()
router.register(r"", PostViewSet)

urlpatterns = [
    path(
        "savedposts/<str:username>/",
        FavoritedSavedPostsAPI.as_view(),
        name="saved",
    ),
    path(
        "comment/reply/update/<str:cid>/",
        ReplyCommentUpdateAPI.as_view(),
        name="reply_update",
    ),
    path(
        "comment/reply/likers/<str:cid>/",
        ReplyCommentLikersAPI.as_view(),
        name="reply_likers",
    ),
    path("comment/reply/like/", LikeCommentReplyAPI.as_view(), name="reply_like"),
    path("comment/reply/<str:pid>/", ReplyCommentAPI.as_view(), name="reply"),
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
    path("search/tag/", SearchPostInTag.as_view(), name="search_tag"),
    path("search/user/", SearchPostInUser.as_view(), name="search_post"),
    path("search/", SearchPost.as_view(), name="search_post"),
    path("images/clear/<str:id>/", clear_images, name="clear_images"),
    path("images/", ImageItemAPI.as_view(), name="post_images"),
    path("likers/<str:pid>/", PostLikersAPI.as_view(), name="post_likers"),
]
urlpatterns += router.urls
