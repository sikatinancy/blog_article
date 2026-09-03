# blog_articles/newsletter/admin.py
from django.contrib import admin
from .models import Article, Subscriber, Subscription


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at')
    list_filter = ('author', 'published_at')
    search_fields = ('title', 'content', 'author__username', 'author__email')
    date_hierarchy = 'published_at'


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    date_hierarchy = 'subscribed_at'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author', 'subscribed_at')
    list_filter = ('author',)
    search_fields = ('subscriber__email', 'author__username')
    date_hierarchy = 'subscribed_at'