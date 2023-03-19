import os
import random
import secrets
from uuid import uuid4

import PIL

# import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import onDelete, ThemeChoices, BaseUser, Profile


# models


class PageSettings(models.Model):

    # fileds
    user = models.OneToOneField(
        get_user_model(), on_delete=onDelete, related_name="page_settings"
    )

    theme = models.CharField(
        choices=ThemeChoices.choices, default=ThemeChoices.light, max_length=5
    )
    show_owners = models.BooleanField(default=True)

    show_photo_logout = models.BooleanField(default=True)

    hide_content = models.BooleanField(default=True)

    followers_limit = models.BooleanField(default=False)

    followers_limit_num = models.IntegerField(default=-1)

    def __str__(self):
        return f"settings for {self.user.username} "


class Category(models.Model):
    name = models.CharField(max_length=40, primary_key=True)

    def __str__(self):
        return self.name


class Page(BaseUser):
    user = models.OneToOneField(
        get_user_model(), on_delete=onDelete, related_name="page"
    )
    # followers_page = models.ManyToManyField(
    #     get_user_model(), related_name="followers_page", blank=True
    # )
    owners = models.ManyToManyField(
        get_user_model(), related_name="owners_page", blank=True
    )
    about = models.CharField(max_length=50)
    categories = models.ManyToManyField(
        Category, related_name="page_categories", blank=True
    )

    def __str__(self):
        return f"{self.user.username} page"
