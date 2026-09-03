# blog_articles/newsletter/api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.get_full_name().strip() or obj.username

    class Meta:
        model = User
        fields = ['id', 'name', 'article_count']