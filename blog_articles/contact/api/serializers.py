# blog_articles/contact/serializers.py
from rest_framework import serializers
from blog_articles.contact.models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    recipient_email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = ContactMessage
        fields = ['id', 'subject', 'message', 'is_read', 'reply', 'created_at', 'recipient_email', 'username']

    def get_recipient_email(self, obj):
        return obj.get_recipient_email()

    def get_username(self, obj):
        return obj.user.username if obj.user else "Anonyme"