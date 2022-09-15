from django.contrib import admin

from .models import ChatRoom, Contact, GroupChatRoom, Message


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["user", "updated", "to"]
    list_filter = ["updated"]


admin.site.register(Message)
# admin.site.register(Contact)
admin.site.register(ChatRoom)
admin.site.register(GroupChatRoom)
