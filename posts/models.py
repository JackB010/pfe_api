import secrets, os

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from accounts.models import PrivacieLevels, onDelete


def img_item(instance, filename):
    ext = filename.split(".")[-1]
    upload_to = f"Images/{instance.user.username}/"
    file_name = f"{instance.id}__{secrets.token_hex(10)}.{ext}"
    return os.path.join(upload_to, file_name)


class Tag(models.Model):
    name = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self, *args, **kwargs):
        return self.name


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
    content = models.TextField(blank=False, null=False)
    images = models.ManyToManyField(ImageItem, related_name="images_group", blank=True)
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
        return CommentPost.objects.filter(Q(post__id=self.id) & Q(deleted=False))

    def __str__(self, *args, **kwargs):
        return f"{self.content[:20]} by {self.user.username}"

    def save(self, *args, **kwargs):
        if self.id == None or self.id == "":
            self.id = secrets.token_hex(16)

        return super().save(*args, **kwargs)


class PostByOwner(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=onDelete, related_name="post_in_pages"
    )
    post = models.ForeignKey("Post", on_delete=onDelete)
    page = models.ForeignKey(
        get_user_model(), on_delete=onDelete, related_name="owner_post"
    )

    class Meta:
        unique_together = ["user", "post"]


class CommentPost(models.Model):
    id = models.CharField(max_length=32, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    post = models.ForeignKey("Post", on_delete=onDelete)
    likes = models.ManyToManyField(
        get_user_model(), related_name="comment_post_liked", blank=True
    )
    reply = models.ManyToManyField("self", blank=True)
    comment = models.TextField(blank=False, null=False)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self, *args, **kwargs):
        return self.comment[:20]

    @property
    def replies(self, *args, **kwargs):
        return CommentReply.objects.filter(Q(comment__id=self.id) & Q(deleted=False))

    def save(self, *args, **kwargs):
        if self.id == None or self.id == "":
            self.id = secrets.token_hex(16)

        return super().save(*args, **kwargs)


class CommentReply(models.Model):
    id = models.CharField(max_length=32, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=onDelete)
    comment = models.ForeignKey("CommentPost", on_delete=onDelete)
    likes = models.ManyToManyField(
        get_user_model(), related_name="comment_reply_liked", blank=True
    )
    reply = models.TextField(blank=False, null=False)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self, *args, **kwargs):
        return self.reply[:20]

    def save(self, *args, **kwargs):
        if self.id == None or self.id == "":
            self.id = secrets.token_hex(16)

        return super().save(*args, **kwargs)
