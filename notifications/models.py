from django.contrib.auth import get_user_model
from django.db import models

from accounts.models import onDelete
from images.models import Image
from posts.models import Post


class Notification(models.Model):
    class NotificationChoices(models.TextChoices):
        liked = "liked"
        commented = "commented"
        comment_liked = "comment_liked"
        followed = "followed"

    to_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, blank=True
    )

    post = models.ForeignKey(Post, on_delete=onDelete, null=True, blank=True)
    image = models.ForeignKey(Image, on_delete=onDelete, null=True, blank=True)
    followedby = models.ForeignKey(
        get_user_model(),
        on_delete=onDelete,
        null=True,
        blank=True,
        related_name="followedby",
    )
    deleted = models.BooleanField(default=False)
    action = models.CharField(choices=NotificationChoices.choices, max_length=13)
    seen = models.BooleanField(default=False)

    def __str__(self, *args, **kwargs):
        return f"{self.created_by} {self.action} {self.to_user} "
