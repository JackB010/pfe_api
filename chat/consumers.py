import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import ChatRoom, Contact, Message
from chat.api.serializers import ImageChatSerializer
User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def message_to_json(self, message):
        return {
            "id": message.id,
            "sender": message.sender.username,
            "content": "Message deleted" if message.deleted else message.content,
            "timestamp": str(message.timestamp),
            "seen": message.seen,
            "photos":ImageChatSerializer(message.photos.all(), many=True).data,
            "deleted": message.deleted,
        }

    def messages_to_json(self, messages):
        return [self.message_to_json(message) for message in messages]

    def fetch_messages(self, data):
        user = self.scope["user"]
        to = User.objects.get(username=data["to"])

        obj1 = Contact.objects.get(user=user, to=to).messages.all()
        obj2 = Contact.objects.get(user=to, to=user).messages.all()

        messages = obj1.union(obj2).order_by("-timestamp")[:8][::-1]

        content = {"message": self.messages_to_json(messages), "type": "fetch_messages"}
        if to.is_active == False:
            self.send_message({"message": None, "type": "fetch_messages"})
        else:
            self.send_message(content)

    def new_message(self, data):
        user = self.scope["user"]
        to = User.objects.get(username=data["to"])
        message = Message(sender=user, content=data["message"])
        message.save()
        obj = Contact.objects.get(user=user, to=to)
        obj.messages.add(message)
        obj.save()
        content = {"message": self.message_to_json(message), "type": "new_message"}
        self.send_chat_message(content)

    def delete_message(self, data):
        user = self.scope["user"]
        mid = data["mid"]

        msg = Message.objects.get(id=mid)
        print(msg)
        msg.deleted = True
        msg.save()
        content = {"message": self.message_to_json(msg), "type": "delete_message"}
        self.send_chat_message(content)

    def make_messages_seen(self, data):
        user = self.scope["user"]
        to = User.objects.get(username=data["to"])
        Contact.objects.get(user=to, to=user).messages.all().update(seen=True)
        self.send_chat_message({"message": to.username, "type": "make_messages_seen"})

    def make_message_seen(self, data):
        msg = Message.objects.filter(id=data["id"])
        msg.update(seen=True)
        self.send_chat_message(
            {"message": self.message_to_json(msg.first()), "type": "make_message_seen"}
        )

    commands = {
        "fetch_messages": fetch_messages,
        "new_message": new_message,
        "delete_message": delete_message,
        "make_messages_seen": make_messages_seen,
        "make_message_seen": make_message_seen,
    }

    def connect(self):
        user1 = self.scope["user"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        user2 = (
            get_user_model()
            .objects.filter(Q(username=self.username) & Q(is_active=True))
            .first()
        )

        if user2 == None or self.username == user1.username:
            self.room_group_name = f"chat_none"
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.close()
            return
        else:
            room = ChatRoom.objects.filter(
                (Q(user1=user1) & Q(user2=user2)) | (Q(user1=user2) & Q(user2=user1))
            ).first()
            if room == None:
                Contact(user=user1, to=user2).save()
                Contact(user=user2, to=user1).save()
                room = ChatRoom(user1=user1, user2=user2)
                room.save()

            self.room_group_name = f"chat_{room.id}"
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands.get(data["command"])(self, data)

    def send_chat_message(self, content):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "send_message", "message": content}
        )

    def send_message(self, content):
        self.send(text_data=json.dumps(content))
