from rest_framework import serializers
from blog_articles.contact.models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'subject', 'message', 'is_read', 'reply']