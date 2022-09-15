import secrets
from accounts.models import onDelete
from django.contrib.auth import get_user_model
from django.db import models


class Message(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)

    class Meta:
        pass
        # ordering=["-timestamp",]

    def __str__(self):
        return self.content[:20]


class Contact(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="from_u"
    )
    to = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="to"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    messages = models.ManyToManyField(Message, related_name="messages", blank=True)

    class Meta:
        ordering = [
            "-updated",
        ]

    def __str__(self):
        return f"from {self.user.username} to {self.to.username}"


class ChatRoom(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    user1 = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user1"
    )
    user2 = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user2"
    )
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.id = secrets.token_hex()

        return super().save(*args, **kwargs)


class GroupChatRoom(models.Model):
    id = models.CharField(max_length=80, primary_key=True, editable=False)
    name = models.CharField(max_length=150)
    creater = models.ForeignKey(get_user_model(), on_delete=onDelete)
    users = models.ManyToManyField(get_user_model(), related_name="group_users")
    messages = models.ManyToManyField(
        Message, related_name="group_messages", blank=True
    )
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.id = secrets.token_hex(40)

        return super().save(*args, **kwargs)
