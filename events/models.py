import os
import random, datetime
import secrets
from uuid import uuid4

# import pytz
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from accounts.models import onDelete
from pages.models import Page


def img_item(instance, filename):
    ext = filename.split(".")[-1]
    upload_to = f"{instance.__class__.__name__}/{instance.user.username}/"
    file_name = f"{instance.id}__{secrets.token_hex(10)}.{ext}"
    return os.path.join(upload_to, file_name)


class BaseEvent(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    action_date = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField("created", auto_now_add=True)

    class Meta:
        abstract = True

    @property
    def done(self):
        if (
          timezone.now()   > self.action_date
        ):
            return True
        return False


class ImageEvent(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    photo = models.ImageField(
        upload_to=img_item,
        blank=True,
        null=True,
    )

    def clean(self, *args, **kwargs):
        if self.photo.width <= 300 or self.photo.height <= 300:
            raise ValidationError(_(f"{self.photo.name}  size not valid "))


class Event(BaseEvent):
    content = models.TextField()
    photos = models.ManyToManyField(ImageEvent, related_name="event_images", blank=True)

    def __str__(self):
        return self.content[:50]



class EventByOwner(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=onDelete, related_name="event_in_pages"
    )
    event = models.ForeignKey("Event", on_delete=onDelete)
    page = models.ForeignKey(
        get_user_model(), on_delete=onDelete, related_name="owner_event"
    )

    class Meta:
        unique_together = ["user", "event"]


class Choice(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Poll(BaseEvent):
    question = models.CharField(max_length=200)
    choices = models.ManyToManyField(Choice, related_name="poll_choice", blank=False)

    def __str__(self):
        return self.question[:50]


class Vote(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    poll = models.ForeignKey(Poll, on_delete=onDelete)
    choice = models.ForeignKey(Choice, on_delete=onDelete)

    class Meta:
        unique_together = ["user", "poll", "choice"]

    def __str__(self):
        return f"{self.user.username} voted in {self.poll} with {self.choice}"
