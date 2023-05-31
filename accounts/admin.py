from django.contrib import admin

from .models import Profile  # LoginModel,
from .models import FollowRelationShip, ProfileSettings, ResetPassword, ConformAccount


@admin.register(ResetPassword)
class LoginModelAdmin(admin.ModelAdmin):
    list_display = ["username_email", "code"]


# @admin.register(ConformAccount)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ["user__username", "code"]
#     search_fields = ["user__username"]

admin.site.register(Profile)
admin.site.register(ProfileSettings)
admin.site.register(FollowRelationShip)
admin.site.register(ConformAccount)
