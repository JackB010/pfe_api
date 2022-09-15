import os
import secrets

from django.contrib.auth import get_user_model
from django.db import models

from accounts.models import PrivacieLevels, onDelete
from posts.models import Tag


def img_item(instance, filename):
    ext = filename.split(".")[-1]
    upload_to = f"Images/{instance.user.username}/"
    file_name = f"{instance.id}__{secrets.token_hex(10)}.{ext}"
    return os.path.join(upload_to, file_name)


class ImageItem(models.Model):
    id = models.CharField(max_length=32, primary_key=True, unique=True, editable=False)
    image = models.ImageField(blank=False, null=False, upload_to=img_item)
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self, *args, **kwargs):
        return self.id

    def save(self, *args, **kwargs):
        if self.id == None or self.id == "":
            self.id = secrets.token_hex(16)

        return super().save(*args, **kwargs)


class Image(models.Model):
    id = models.CharField(max_length=32, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    images = models.ManyToManyField(ImageItem, related_name="images_group")
    content = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(
        get_user_model(), related_name="images_liked", blank=True
    )
    saved = models.ManyToManyField(
        get_user_model(), related_name="images_saved", blank=True
    )
    favorited = models.ManyToManyField(
        get_user_model(), related_name="images_favorited", blank=True
    )
    tags = models.ManyToManyField(Tag, related_name="images", blank=True)

    show_image_to = models.CharField(
        choices=PrivacieLevels.choices, default=PrivacieLevels.everyone, max_length=9
    )
    allow_comments = models.BooleanField(default=True)

    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "-updated",
        ]

    @property
    def comments(self, *args, **kwargs):
        return CommentImage.objects.filter(image__id=self.id)

    def __str__(self, *args, **kwargs):
        return (
            f"{self.content[:20]} by {self.user.username}"
            if self.content != None
            else f"Image by {self.user}"
        )

    def save(self, *args, **kwargs):
        if self.id == None or self.id == "":
            self.id = secrets.token_hex(16)

        return super().save(*args, **kwargs)


class CommentImage(models.Model):
    id = models.CharField(max_length=32, primary_key=True, unique=True, editable=False)
    image = models.ForeignKey(Image, on_delete=onDelete)
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    likes = models.ManyToManyField(
        get_user_model(), related_name="comment_image_liked", blank=True
    )
    deleted = models.BooleanField(default=False)
    comment = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self, *args, **kwargs):
        return self.comment[:20]

    def save(self, *args, **kwargs):
        if self.id == None or self.id == "":
            self.id = secrets.token_hex(16)

        return super().save(*args, **kwargs)
