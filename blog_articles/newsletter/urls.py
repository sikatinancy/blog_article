# blog_articles/newsletter/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.viewsets import NewsletterAPI
from blog_articles.newsletter.views.start import start_subscription
from blog_articles.newsletter.views.confirm import confirm_subscription
from blog_articles.newsletter.views.unsubscribe import unsubscribe

# Router pour API REST (recommandé)
router = DefaultRouter()
router.register(r'', NewsletterAPI, basename='newsletter')

urlpatterns = [
    # API REST
    path('', include(router.urls)),

    # Vues classiques (fallback ou accès direct)
    path('start/', start_subscription, name='newsletter-start'),
    path('confirm/', confirm_subscription, name='newsletter-confirm'),
    path('unsubscribe/', unsubscribe, name='newsletter-unsubscribe'),
]