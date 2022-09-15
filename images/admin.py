from django.contrib import admin

from .models import CommentImage, Image, ImageItem

# Register your models here.


class CommentInLines(admin.TabularInline):
    model = CommentImage


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("content", "updated", "user")
    list_filter = ("deleted", "show_image_to")
    ordering = ("-updated",)
    filter_horizontal = ("tags",)
    search_fields = ("content",)
    inlines = [
        CommentInLines,
    ]


admin.site.register(ImageItem)
