# Generated by Django 4.1 on 2023-03-19 19:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import posts.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CommentPost",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("comment", models.TextField()),
                ("deleted", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "likes",
                    models.ManyToManyField(
                        blank=True,
                        related_name="comment_post_liked",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ImageItem",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("image", models.ImageField(upload_to=posts.models.img_item)),
                ("deleted", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=40)),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "show_post_to",
                    models.CharField(
                        choices=[
                            ("everyone", "Everyone"),
                            ("followers", "Followers"),
                            ("onlyme", "Onlyme"),
                        ],
                        default="everyone",
                        max_length=9,
                    ),
                ),
                ("content", models.TextField()),
                ("allow_comments", models.BooleanField(default=True)),
                ("deleted", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "favorited",
                    models.ManyToManyField(
                        blank=True,
                        related_name="posts_favorited",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "images",
                    models.ManyToManyField(
                        blank=True, related_name="images_group", to="posts.imageitem"
                    ),
                ),
                (
                    "likes",
                    models.ManyToManyField(
                        blank=True,
                        related_name="posts_liked",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "saved",
                    models.ManyToManyField(
                        blank=True,
                        related_name="posts_saved",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        blank=True, related_name="posts", to="posts.tag"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-updated"],
            },
        ),
        migrations.CreateModel(
            name="CommentReply",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("reply", models.TextField()),
                ("deleted", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="posts.commentpost",
                    ),
                ),
                (
                    "likes",
                    models.ManyToManyField(
                        blank=True,
                        related_name="comment_reply_liked",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="commentpost",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="posts.post"
            ),
        ),
        migrations.AddField(
            model_name="commentpost",
            name="reply",
            field=models.ManyToManyField(blank=True, to="posts.commentpost"),
        ),
        migrations.AddField(
            model_name="commentpost",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.CreateModel(
            name="PostByOwner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owner_post",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="posts.post"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_in_pages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "post")},
            },
        ),
    ]
