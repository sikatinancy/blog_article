from django.db import models
from django.conf import settings



class ContactMessage(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages"
    )

    email = models.EmailField(
        "Email de contact",
        blank=True,
        null=True
    )

    subject = models.CharField(
        "Sujet",
        max_length=255
    )

    message = models.TextField(
        "Message"
    )

    reply = models.TextField(
        "Réponse admin",
        blank=True,
        null=True
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = [
            "-created_at"
        ]


    def __str__(self):
        return self.subject





# ==================================================
# CHAT
# ==================================================


class Conversation(models.Model):

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chat_conversations"
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "-updated_at"
        ]



    def __str__(self):

        users = self.participants.all()

        return " - ".join(
            user.username
            for user in users
        )





class ChatMessage(models.Model):


    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )


    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_chat_messages"
    )


    content = models.TextField()



    created_at = models.DateTimeField(
        auto_now_add=True
    )


    is_read = models.BooleanField(
        default=False
    )


    class Meta:

        ordering = [
            "created_at"
        ]



    def __str__(self):

        return (
            f"{self.sender.username}: "
            f"{self.content[:30]}"
        )