from django.contrib import admin

from .models import CommentPost, Post, Tag, ImageItem, PostByOwner, CommentReply


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "created"]
    search_fields = ("name",)
    ordering = ("-created",)


admin.site.register(CommentPost)
admin.site.register(PostByOwner)
admin.site.register(ImageItem)
admin.site.register(CommentReply)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("content", "updated", "user")
    list_filter = ("deleted", "show_post_to")
    ordering = ("-updated",)
    filter_horizontal = ("tags",)
    search_fields = ("content",)
