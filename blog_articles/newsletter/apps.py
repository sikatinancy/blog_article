# blog_articles/newsletter/apps.py
from django.apps import AppConfig

class NewsletterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_articles.newsletter'  # <-- Chemin complet
    label = 'newsletter'               # <-- Nom court (optionnel mais recommandé)