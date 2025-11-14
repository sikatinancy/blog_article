# blog_articles/newsletter/api/serializers.py
from rest_framework import serializers
from ..models import Author

class AuthorSerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'article_count']