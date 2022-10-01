from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters, generics, pagination, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.api.permissions import IsCreaterOrReadOnly
from accounts.api.serializers import UserShortSerializer
from accounts.models import FollowRelationShip, Profile
from notifications.models import Notification
from posts.models import CommentPost, Post

from .serializers import CommentSerializer, LSFSerializer, PostSerializer


class PostLikersAPI(generics.ListAPIView):
    serializer_class = UserShortSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("pid")
        post = Post.objects.filter(id=id).first()
        return [i.profile for i in post.likes.all()]


class CommentLikersAPI(generics.ListAPIView):
    serializer_class = UserShortSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        comment = CommentPost.objects.filter(id=id).first()
        return [i.profile for i in comment.likes.all()]


class PostCommentUpdateAPI(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    queryset = CommentPost.objects.all()
    permission_classes = [IsAuthenticated, IsCreaterOrReadOnly]

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        return get_object_or_404(CommentPost, Q(id=id) & Q(deleted=False))


class PostCommentAPI(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("pid")
        return get_object_or_404(Post, id=id).comments.filter(deleted=False).order_by("-created")

    # def post(self, request, *args, **kwargs):
    #     data = request.data
    #     data = self.get_serializer(data=data)
    #     if data.is_valid():
    #         data = data.data
    #         id = self.kwargs.get("pid")
    #         post = get_object_or_404(Post,id = id)
    #         comment = CommentPost(
    #                     content=data["comment"],
    #                     post=post,
    #                     user=request.user
    #                     )
    #         comment.save()
    #         return Response(comment)
    #     return Response({"errors": data.errors})


class LikePostCommentAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            comment = CommentPost.objects.filter(id=id).first()
            if request.user in comment.likes.all():
                comment.likes.remove(request.user)
            else:
                comment.likes.add(request.user)
                post = comment.post
                notification = Notification.objects.create(
                    to_user=post.user,
                    created_by=request.user,
                    action=Notification.NotificationChoices.comment_liked,
                    post=comment.post,
                )
                notification.save()
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )


class LikePostAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            post = Post.objects.filter(id=id).first()
            if request.user in post.likes.all():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
                notification = Notification.objects.create(
                    to_user=post.user,
                    created_by=request.user,
                    action=Notification.NotificationChoices.liked,
                    post=post,
                )
                notification.save()
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )


class SavePostAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            post = Post.objects.filter(id=id).first()
            if request.user in post.saved.all():
                post.saved.remove(request.user)
            else:
                post.saved.add(request.user)
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )


class FavoritePostAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            post = Post.objects.filter(id=id).first()
            if request.user in post.favorited.all():
                post.favorited.remove(request.user)
            else:
                post.favorited.add(request.user)
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )


class FollowingPostsAPI(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self, *args, **kwargs):
        p = FollowRelationShip.objects.filter(user=self.request.user)
        p = [i.following for i in p]
        return Post.objects.filter(Q(deleted=False) & Q(user__in=p) & Q(show_post_to__in=['everyone', 'followers']))


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(deleted=False)
    permission_classes = [
        IsCreaterOrReadOnly,
        IsAuthenticated,
    ]
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username",]
    def get_object(self):
        queryset = self.get_queryset()
        id = self.kwargs.get("pk")        
        obj = get_object_or_404(Post, id=id)
        # self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        search = self.request.query_params.get("search")
        if user.profile.user.username == search:
            return Post.objects.filter(Q(deleted=False) & Q(user=user))
        else:
            profile = Profile.objects.filter(user__username=search).first()
            if profile != None:
                if user in profile.followers_profile.all():
                    return  Post.objects.filter(Q(deleted=False) & Q(show_post_to__in=['everyone', 'followers']) & Q(user=profile.user))
                else:
                    return  Post.objects.filter(Q(deleted=False) & Q(show_post_to__in=['everyone']) & Q(user=profile.user))
        return Post.objects.none()

class SearchPost(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["content"]
    serializer_class = PostSerializer
    queryset = Post.objects.filter(deleted=False)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        search = self.request.query_params.get("search")
        if search == None :
            return Post.objects.none()
        posts = Post.objects.filter(Q(deleted=False) & Q(show_post_to__in=['everyone']) & Q(content__icontains=search))
        return  posts
        









