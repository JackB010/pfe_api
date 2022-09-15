import secrets

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from accounts.models import PrivacieLevels, onDelete


class Tag(models.Model):
    name = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self, *args, **kwargs):
        return self.name


class Post(models.Model):
    id = models.CharField(max_length=32, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    likes = models.ManyToManyField(
        get_user_model(), related_name="posts_liked", blank=True
    )
    saved = models.ManyToManyField(
        get_user_model(), related_name="posts_saved", blank=True
    )
    favorited = models.ManyToManyField(
        get_user_model(), related_name="posts_favorited", blank=True
    )

    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    show_post_to = models.CharField(
        choices=PrivacieLevels.choices, default=PrivacieLevels.everyone, max_length=9
    )
    allow_comments = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    content = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "-updated",
        ]

    @property
    def comments(self, *args, **kwargs):
        return CommentPost.objects.filter(Q(post__id=self.id) & Q(deleted=False))

    def __str__(self, *args, **kwargs):
        return f"{self.content[:20]} by {self.user.username}"

    def save(self, *args, **kwargs):
        if self.id == None or self.id == "":
            self.id = secrets.token_hex(16)

        return super().save(*args, **kwargs)


class CommentPost(models.Model):
    id = models.CharField(max_length=32, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    post = models.ForeignKey("Post", on_delete=onDelete)
    likes = models.ManyToManyField(
        get_user_model(), related_name="comment_post_liked", blank=True
    )
    comment = models.TextField(blank=False, null=False)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self, *args, **kwargs):
        return self.comment[:20]

    def save(self, *args, **kwargs):
        if self.id == None or self.id == "":
            self.id = secrets.token_hex(16)

        return super().save(*args, **kwargs)
