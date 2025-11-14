# blog_articles/newsletter/admin.py
from django.contrib import admin
from .models import Author, Article, Subscriber, Subscription

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'article_count')
    search_fields = ('name', 'email')
    readonly_fields = ('article_count',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at')
    search_fields = ('title', 'content')
    list_filter = ('author', 'published_at')
    date_hierarchy = 'published_at'

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    date_hierarchy = 'subscribed_at'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author', 'subscribed_at')
    search_fields = ('subscriber__email', 'author__name')
    list_filter = ('author',)
    date_hierarchy = 'subscribed_at'