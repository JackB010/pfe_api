from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import  get_object_or_404
from rest_framework import filters, generics, pagination, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view


from accounts.api.permissions import IsCreaterOrReadOnly
from accounts.api.serializers import UserShortSerializer
from pages.api.serializers import PageShortSerializer
from accounts.api.views import check_type
from accounts.models import FollowRelationShip, Profile
from notifications.models import Notification
from posts.models import CommentPost, Post, PostByOwner, CommentReply, ImageItem

from .serializers import CommentSerializer, LSFSerializer, PostSerializer, ReplyCommentSerializer, ImageItemSerializer

@api_view([ 'POST'])
def clear_images(request, id=None,pid=None, *args, **kwargs):
    img = ImageItem.objects.get(id=id, deleted=False, user__is_active=True)
    img.deleted = True;
    img.save()
    return Response({"status": status.HTTP_200_OK})

class ImageItemAPI(generics.CreateAPIView):
    serializer_class = ImageItemSerializer
    queryset = ImageItem.objects.filter(deleted=False)
    permission_classes = [
        IsAuthenticated,
    ]


class LikeCommentReplyAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            reply = CommentReply.objects.filter(Q(id=id) & Q(deleted=False) & Q(user__is_active=True)).first()
            if request.user in reply.likes.all():
                reply.likes.remove(request.user)
            else:
                reply.likes.add(request.user)
                # comment = reply.comment
                if(reply.user != request.user):
                    notification,created = Notification.objects.update_or_create(
                    to_user=reply.user,
                    created_by=request.user,
                    action=Notification.NotificationChoices.reply_liked,
                    reply=reply,
                )
                    notification.save()
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )






class ReplyCommentLikersAPI(generics.ListAPIView):

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        reply = CommentReply.objects.filter(Q(id=id) & Q(deleted=False)& Q(user__is_active=True)).first()
        return reply

    def get(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        reply = CommentReply.objects.filter(id=id).first()
        likes = []
        if reply:
            for i in reply.likes.all():
                if (check_type(i.username)=="profile"):
                    likes.append(UserShortSerializer(i.profile, context={"request": self.request}).data)
                else:
                    likes.append(PageShortSerializer(i.page, context={"request": self.request}).data)
        return Response(likes)

class ReplyCommentUpdateAPI(generics.UpdateAPIView):
    serializer_class = ReplyCommentSerializer
    queryset = CommentReply.objects.filter(deleted=False)
    permission_classes = [IsAuthenticated, IsCreaterOrReadOnly]

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        return get_object_or_404(self.get_queryset(), id=id)


class ReplyCommentAPI(generics.ListCreateAPIView):
    serializer_class = ReplyCommentSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("pid")
        return (
            get_object_or_404(CommentPost, id=id)
            .replies.filter(deleted=False)
            .order_by("-created")
        )



class PostLikersAPI(generics.GenericAPIView):
    # serializer_class = UserShortSerializer
    queryset = Post.objects.all()

    def get(self, request, *args, **kwargs):
        request = self.request
        id = self.kwargs.get("pid")
        post = Post.objects.filter(id=id).first()
        profiles = []
        pages = []
        if post:
            for i in post.likes.all():
                if check_type(i.username) == "profile":
                    profiles.append(i.profile)
                else:
                    pages.append(i.page)
        return Response(
            {
                "pages": PageShortSerializer(
                    pages, many=True, context={"request": request}
                ).data,
                "profiles": UserShortSerializer(
                    profiles, many=True, context={"request": request}
                ).data,
            }
        )


class CommentLikersAPI(generics.ListAPIView):

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        comment = CommentPost.objects.filter(Q(id=id)).first()
        return comment
    def get(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        comment = CommentPost.objects.filter(Q(id=id)).first()
        likes = []
        if comment:
            for i in comment.likes.all():
                if (check_type(i.username)=="profile"):
                    likes.append(UserShortSerializer(i.profile, context={"request": self.request}).data)
                else:
                    likes.append(PageShortSerializer(i.page, context={"request": self.request}).data)
        return Response(likes)

class PostCommentUpdateAPI(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    queryset = CommentPost.objects.filter(Q(deleted=False)& Q(user__is_active=True))
    permission_classes = [IsAuthenticated, IsCreaterOrReadOnly]

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        queryset = CommentPost.objects.filter(Q(deleted=False)& Q(user__is_active=True))
        return get_object_or_404(queryset, id=id)


class PostCommentAPI(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("pid")
        return (
            get_object_or_404(Post, id=id)
            .comments.filter(Q(deleted=False)& Q(user__is_active=True))
            .order_by("-created")
        )

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
                if(request.user != comment.user):
                    notification,created = Notification.objects.update_or_create(
                    to_user=comment.user,
                    created_by=request.user,
                    action=Notification.NotificationChoices.comment_liked,
                    post=comment.post,
                    comment=comment,

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
            post = Post.objects.filter(id=id, deleted=False, user__is_active=True).first()
            if request.user in post.likes.all():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
                if(post.user != request.user):
                    notification,created = Notification.objects.update_or_create(
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
            post = Post.objects.filter(id=id, deleted=False, user__is_active=True).first()
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
class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10

class FavoritedSavedPostsAPI(generics.ListAPIView):
    serializer_class = PostSerializer
    # get_queryset = Post.objects.filter(Q(deleted=False) & Q(user__is_active=True))
    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        username = self.request.parser_context['kwargs']['username']
        user1 = get_user_model().objects.filter(Q(username=username) & Q(is_active=True)).first()
        data =  Post.objects.none()
        if(user1==None):
            return data
        if(user != user1):
            if(check_type(user1) == 'page'):
                if(user in user1.page.owners.all()):
                    data =  user1.posts_saved.filter(Q(deleted=False) & Q(user__is_active=True))
                    
        else:
            data =  user.posts_saved.filter(Q(deleted=False) & Q(user__is_active=True))
        following = user.following.all().values("following")

        posts_m = data.filter(
                Q(user=user)
                & Q(deleted=False)
                & Q(show_post_to__in=["onlyme"])
                & Q(user__is_active=True)
                )
        posts_f = data.filter(
                Q(user__in=following)
                & Q(deleted=False)
                & Q(show_post_to__in=["followers"])
                & Q(user__is_active=True)
            )
        posts = data.filter(
                Q(deleted=False)
                & Q(show_post_to__in=["everyone"])
                & Q(user__is_active=True)
            )
        return posts_m | posts_f | posts

    # def get(self, request, username=None, *args, **kwargs):
    #     user = request.user
    #     user1 = get_user_model().objects.filter(Q(username=username) & Q(is_active=True)).first()
    #     data =  Post.objects.none()
    #     if(user1==None):
    #         return Response(data)
    #     if(user != user1):
    #         if(check_type(user1) == 'page'):
    #             if(user in user1.page.owners.all()):
    #                 data =  user1.posts_saved.filter(Q(deleted=False) & Q(user__is_active=True))
    #     else:
    #         data =  user.posts_saved.filter(Q(deleted=False) & Q(user__is_active=True))
    #     data = PostSerializer(data=data, many=True,context={"request": request})
    #     data.is_valid()
    #     return Response(data.data)




class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(deleted=False)
    pagination_class = StandardResultsSetPagination

    permission_classes = [
        # IsCreaterOrReadOnly,
        # IsAuthenticated,
    ]
    filter_backends = [filters.SearchFilter]
    search_fields = ["content", "user__username", "tags__name"]

    def get_object(self):
        id = self.kwargs.get("pk")
        obj = get_object_or_404(Post, Q(deleted=False) & Q(pk=id) & Q(user__is_active=True))
        obj.images.set(obj.images.filter(deleted=False))
        return obj

    def get_queryset(self, *args, **kwargs):
        user1 = self.request.user
        search = self.request.query_params.get("search")
        user = self.request.query_params.get("user")
        user = get_user_model().objects.filter(username=user, is_active=True).first()
        print(user,search)
        if(user1.id != None):
            posts_m = Post.objects.filter(
                        Q(user=user1)
                        & Q(user__is_active=True)
                        & Q(deleted=False)
                        & Q(show_post_to__in=["onlyme"])
                    )
            if user == None:
                following = user1.following.filter(following__is_active=True).values("following")
                posts_f = Post.objects.filter(
                    Q(deleted=False)
                    & Q(user__in=following)
                    & Q(show_post_to__in=["everyone", "followers"])
                    & Q(user__is_active=True)
                )
                return (posts_m | posts_f).order_by('-created')
            else:
                posts_f = Post.objects.filter(
                    Q(deleted=False)
                    & Q(user=user)
                    & Q(show_post_to__in=["everyone", "followers"])
                    & Q(user__is_active=True)
                )
                if(user==user1):
                    return (posts_m | posts_f).order_by('-created')
                return posts_f.order_by('-created')
        else:
            if check_type(user) == "page" and user!=None:
                return Post.objects.filter(
                    Q(deleted=False)
                    & Q(user=user)
                    & Q(show_post_to__in=["everyone"])
                    & Q(user__is_active=True)
                ).order_by('-created')
            else:
                return Post.objects.none()

        # else:
        #     if user.id == None:
        #         if check_type(search) == "page":
        #             return Post.objects.filter(
        #                 Q(deleted=False)
        #                 & Q(show_post_to__in=["everyone"])
        #                 & Q(user__username=search)& Q(user__is_active=True)
        #             )
        #         return Post.objects.none()

        #     target_u = get_user_model().objects.filter(username=search).first()
        #     if(target_u==None):
        #         return Post.objects.none()
        #     f = target_u.following.filter(user=user, following=target_u).count() != 0
        #     if f:
        #         if user == target_u:
        #             PL = ["everyone", "followers", "onlyme"]
        #         else:
        #             PL = ["everyone", "followers"]
        #         return Post.objects.filter(
        #             Q(deleted=False) & Q(show_post_to__in=PL) & Q(user=target_u)& Q(user__is_active=True)
        #         )
        #     else:
        #         return Post.objects.filter(
        #             Q(deleted=False)
        #             & Q(show_post_to__in=["everyone"])
        #             & Q(user=target_u)
        #             & Q(user__is_active=True)
        #         )
        return Post.objects.none()

class SearchPost(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["content", "user__username", "tags__name"]
    serializer_class = PostSerializer
    queryset = Post.objects.filter(deleted=False)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        search = self.request.query_params.get("search")
        if search == None:
            return Post.objects.none()
        if self.request.user.id != None:
            following = user.following.all().values("following")

            posts_m = Post.objects.filter(
                Q(user=user)
                & Q(user__is_active=True)
                & Q(deleted=False)
                & Q(show_post_to__in=["onlyme"])
                &( Q(content__icontains=search)
                | Q(tags__name__icontains=search)
                )
                )
            posts_f = Post.objects.filter(
                Q(user__in=following)
                & Q(user__is_active=True)
                & Q(deleted=False)
                & Q(show_post_to__in=["followers"])
               &( Q(content__icontains=search)
                | Q(tags__name__icontains=search))
            )
            posts = Post.objects.filter(
                Q(deleted=False)
                & Q(user__is_active=True)
                & Q(show_post_to__in=["everyone"])
            & (Q(tags__name__icontains=search) | Q(content__icontains=search)))
            return posts | posts_f | posts_m

        return Post.objects.none()

class SearchPostInUser(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["content", "user__username", "tags__name",]
    serializer_class = PostSerializer
    queryset = Post.objects.filter(deleted=False)
    pagination_class = StandardResultsSetPagination


    def get_queryset(self, *args, **kwargs):
        user = self.request.query_params.get("user")
        user = get_user_model().objects.filter(username=user).first()
        return Post.objects.filter(
                Q(deleted=False) & Q(user=user) & Q(user__is_active=True))

class SearchPostInTag(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["tags__name"]
    serializer_class = PostSerializer
    queryset = Post.objects.filter(deleted=False)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        search = self.request.query_params.get("search")
        if search == None:
            return Post.objects.none()
        if self.request.user.id != None:
            following = user.following.all().values("following")
            posts_m = Post.objects.filter(
                Q(user=user)
                & Q(deleted=False)
                & Q(show_post_to__in=["onlyme"])
                & Q(tags__name__icontains=search)
                & Q(user__is_active=True)
                )
            posts_f = Post.objects.filter(
                Q(user__in=following)
                & Q(deleted=False)
                & Q(show_post_to__in=["followers"])
                & Q(tags__name__icontains=search)
                & Q(user__is_active=True)
            )
            posts = Post.objects.filter(
                Q(deleted=False)
                & Q(show_post_to__in=["everyone"])
                & Q(tags__name__icontains=search)
                & Q(user__is_active=True)
            )
            return posts | posts_f | posts_m

        return Post.objects.none()
        