from django.contrib import admin
from .models import Page, PageSettings, Category

# @admin.register(LoginModel)
# class LoginModelAdmin(admin.ModelAdmin):
#     list_display = ["username_email", "code"]

# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ["user__username", "first_ip"]
#     search_fields = ["user__username"]
#     filter_fields = ["user__username", "country"]

admin.site.register(Page)
admin.site.register(Category)
admin.site.register(PageSettings)
# admin.site.register(FollowRelationShipPage)
