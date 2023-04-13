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


# models functions
def img_profile(instance, filename):
    ext = filename.split(".")[-1]
    upload_to = f"{instance.__class__.__name__}/{instance.id}/"
    file_name = f"{instance.user.username}__{secrets.token_hex(8)}.{ext}"
    return os.path.join(upload_to, file_name)


# models
onDelete = models.CASCADE


class SexChoices(models.TextChoices):
    male = "male"
    female = "female"
    none = "none"


class PrivacieLevels(models.TextChoices):
    everyone = "everyone"
    followers = "followers"
    onlyme = "onlyme"


class FTypeChoices(models.TextChoices):
    user_user = "user_user"
    user_page = "user_page"
    page_page = "page_page"


class ThemeChoices(models.TextChoices):
    dark = "dark"
    light = "light"


class ProfileSettings(models.Model):

    # fileds
    user = models.OneToOneField(
        get_user_model(), on_delete=onDelete, related_name="settings"
    )

    birth_day = models.DateField(_("Birth Day"), blank=True, null=True)

    show_birth_day = models.CharField(
        choices=PrivacieLevels.choices, default=PrivacieLevels.everyone, max_length=9
    )

    show_full_name = models.CharField(
        choices=PrivacieLevels.choices, default=PrivacieLevels.everyone, max_length=9
    )
    show_pages_owned = models.CharField(
        choices=PrivacieLevels.choices, default=PrivacieLevels.everyone, max_length=9
    )

    show_gender = models.CharField(
        choices=PrivacieLevels.choices, default=PrivacieLevels.everyone, max_length=9
    )

    show_favorites = models.CharField(
        choices=PrivacieLevels.choices, default=PrivacieLevels.everyone, max_length=9
    )

    show_photo_profile = models.CharField(
        choices=PrivacieLevels.choices, default=PrivacieLevels.everyone, max_length=9
    )

    gender = models.CharField(
        choices=SexChoices.choices, default=SexChoices.none, max_length=6
    )

    theme = models.CharField(
        choices=ThemeChoices.choices, default=ThemeChoices.light, max_length=5
    )

    show_photo_logout = models.BooleanField(default=True)

    def __str__(self):
        return f"settings for {self.user.username} "


class BaseUser(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        _("picture"),
        upload_to=img_profile,
        default="default/default_photo.jpg",
        blank=True,
        null=True,
    )

    photo_icon = models.ImageField(
        _("profil picture icon"),
        upload_to=img_profile,
        default="default/default_icon.png",
        blank=True,
        null=True,
    )
    # country = models.CharField(
    #     max_length=10, choices=pytz.country_names.items(), blank=True, null=True
    # )
    # blocked = models.ManyToManyField(get_user_model(),related_name='block_list' ,blank=True)
    first_ip = models.GenericIPAddressField(blank=False, editable=False, null=True)
    ip = models.GenericIPAddressField(blank=False, editable=False, null=True)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    last_updated = models.DateTimeField(_("updated"), auto_now=True)
    last_seen = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def clean(self, *args, **kwargs):
        if self.photo.width <= 300 or self.photo.height <= 300:
            raise ValidationError(_(f"{self.photo.name}  size not valid "))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo_icon:
            size = (200, 200)
            img = PIL.Image.open(self.photo_icon.path)
            img.thumbnail(size)
            img.save(self.photo_icon.path)


class Profile(BaseUser):
    user = models.OneToOneField(
        get_user_model(), on_delete=onDelete, related_name="profile"
    )
    # followers_profile = models.ManyToManyField(
    #     get_user_model(), related_name="followers_profile", blank=True
    # )
    # followering_page = models.ManyToManyField(
    #     get_user_model(), related_name="user_foll_page", blank=True
    # )

    def __str__(self):
        return f"{self.user.username} profile"


class FollowRelationShip(models.Model):
    user = models.ForeignKey(
        get_user_model(), related_name="following", on_delete=onDelete
    )
    following = models.ForeignKey(
        get_user_model(), related_name="followed_by", on_delete=onDelete
    )
    ftype = models.CharField(choices=FTypeChoices.choices, max_length=9)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "following"]

    def __str__(self, *args, **kwargs):
        return f"{self.user} following  {self.following}"


class ResetPassword(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    username_email = models.CharField(max_length=100, blank=False, unique=True)
    code = models.CharField(max_length=6, blank=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.code = self.generate_code()
        if self.username_email == None:
            raise ValidationError("Should give username or email to reset password")
        obj = ResetPassword.objects.filter(username_email=self.username_email).first()
        if obj != None:
            obj.delete()
        return super().save(self, *args, **kwargs)

    @property
    def get_new_code(self):
        self.code = generate_code()

    def generate_code(self):
        return random.randint(1000000, 9999999)

    def __str__(self):
        return f" rest for {self.username_email}"
