from django.contrib.auth import get_user_model
from django.db import models

from accounts.models import onDelete

# from images.models import Image
from posts.models import Post, CommentPost, CommentReply
from events.models import Poll, Event


class Notification(models.Model):
    class NotificationChoices(models.TextChoices):
        liked = "liked"
        commented = "commented"
        comment_liked = "comment_liked"
        replied = "replied"
        reply_liked = "reply_liked"
        followed = "followed"
        event = "event"

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
    comment = models.ForeignKey(CommentPost, on_delete=onDelete, null=True, blank=True)
    reply = models.ForeignKey(CommentReply, on_delete=onDelete, null=True, blank=True)
    followedby = models.ForeignKey(
        get_user_model(),
        on_delete=onDelete,
        null=True,
        blank=True,
        related_name="followedby",
    )
    created = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    event_made = models.ForeignKey(Event, on_delete=onDelete, null=True, blank=True)
    poll_made = models.ForeignKey(Poll, on_delete=onDelete, null=True, blank=True)
    deleted = models.BooleanField(default=False)
    action = models.CharField(choices=NotificationChoices.choices, max_length=13)
    seen = models.BooleanField(default=False)

    def __str__(self, *args, **kwargs):
        return f"{self.created_by} {self.action} {self.to_user} "
