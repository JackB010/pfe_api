from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, pagination, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.api.permissions import IsCreaterOrReadOnly
from accounts.api.serializers import UserShortSerializer
from accounts.models import FollowRelationShip, Profile
from images.models import CommentImage, Image, ImageItem
from notifications.models import Notification
from posts.api.serializers import LSFSerializer
from posts.models import Tag

from .serializers import CommentSerializer, ImageSerializer, ImageUpdateSerializer


class ImageLikersAPI(generics.ListAPIView):
    serializer_class = UserShortSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("iid")
        image = Image.objects.filter(id=id).first()
        return [i.profile for i in image.likes.all()]


class CommentLikersAPI(generics.ListAPIView):
    serializer_class = UserShortSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        comment = CommentImage.objects.filter(id=id).first()
        return [i.profile for i in comment.likes.all()]


class ImageCommentUpdateAPI(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    queryset = CommentImage.objects.all()
    permission_classes = [IsAuthenticated, IsCreaterOrReadOnly]

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("cid")
        return get_object_or_404(CommentImage, Q(id=id) & Q(deleted=False))


class ImageCommentAPI(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("iid")
        return get_object_or_404(Image, id=id).comments.filter(deleted=False)


class LikeImageCommentAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            comment = CommentImage.objects.filter(id=id).first()
            if request.user in comment.likes.all():
                comment.likes.remove(request.user)
            else:
                comment.likes.add(request.user)
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


class ImageUpdateAPI(generics.RetrieveUpdateAPIView):
    serializer_class = ImageUpdateSerializer
    permission_classes = [IsAuthenticated, IsCreaterOrReadOnly]

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get("iid")
        return get_object_or_404(Image, Q(deleted=False) & Q(id=id))


### get ###


class FollowingImagesAPI(generics.ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self, *args, **kwargs):
        p = FollowRelationShip.objects.filter(user=self.request.user)
        p = [i.following for i in p]
        print(p)
        return Image.objects.filter(Q(deleted=False) & Q(user__in=p))


# class ImageAPI(generics.ListCreateAPIView):
#     serializer_class = ImageSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ["content", "user__username", "user__profile__id"]

#     def get_queryset(self, *args, **kwargs):
#         return (
#             Image.objects.filter(deleted=False)
#             if self.request.query_params.get("search")
#             else Image.objects.none()
#         )


class ImageAPI(generics.ListCreateAPIView):
    serializer_class = ImageSerializer
    queryset = Image.objects.filter(deleted=False)
    permission_classes = [
        IsCreaterOrReadOnly,
        IsAuthenticated,
    ]
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username",]

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        search = self.request.query_params.get("search")
        if user.profile.user.username == search:
            return Image.objects.filter(Q(deleted=False) & Q(user=user))
        else:
            profile = Profile.objects.filter(user__username=search).first()
            if profile != None:
                if user in profile.followers_profile.all():
                    return  Image.objects.filter(Q(deleted=False) & Q(show_image_to__in=['everyone', 'followers']) & Q(user=profile.user))
                else:
                    return  Image.objects.filter(Q(deleted=False) & Q(show_image_to__in=['everyone']) & Q(user=profile.user))
        return Image.objects.none()

class SearchImage(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["content",]
    serializer_class = ImageSerializer
    queryset = Image.objects.filter(deleted=False)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        search = self.request.query_params.get("search")
        if search == None:
            return Image.objects.none()
        images = Image.objects.filter(Q(deleted=False) & Q(content__icontains=search) & Q(show_image_to__in=['everyone']))
        return  images 


## post ##
class LikeImageAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            image = Image.objects.filter(id=id).first()
            if request.user in image.likes.all():
                image.likes.remove(request.user)
            else:
                image.likes.add(request.user)
                notification = Notification.objects.create(
                    to_user=image.user,
                    created_by=request.user,
                    action=Notification.NotificationChoices.liked,
                    image=image,
                )
                notification.save()
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )


class SaveImageAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            post = Image.objects.filter(id=id).first()
            if request.user in post.saved.all():
                post.saved.remove(request.user)
            else:
                post.saved.add(request.user)
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )


class FavoriteImageAPI(generics.GenericAPIView):
    serializer_class = LSFSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            id = request.data.get("id")
            post = Image.objects.filter(id=id).first()
            if request.user in post.favorited.all():
                post.favorited.remove(request.user)
            else:
                post.favorited.add(request.user)
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )
