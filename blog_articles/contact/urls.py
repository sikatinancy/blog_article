# blog_articles/contact/urls.py
from django.urls import path

# IMPORTS ABSOLUS → ÇA MARCHE À 100%
from blog_articles.contact.views.message_views import (
    MessageCreateView,
    MessageEditView,
    MessageDeleteView,
    MessageDetailView,
    MessageReplyView
)

from .views.chat_views import (
    user_chat_room,
    admin_chat_list,
    admin_chat_room,
)
from blog_articles.contact.api.viewsets import (
    ContactMessageListAPI,
    ContactMessageDetailAPI
)

app_name = 'contact'

urlpatterns = [
    # Vues classiques
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:id>/edit/', MessageEditView.as_view(), name='message_edit'),
    path('messages/<int:id>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('messages/<int:id>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:id>/reply/', MessageReplyView.as_view(), name='message_reply'),

    # API
    path('api/messages/', ContactMessageListAPI.as_view(), name='api_message_list_create'),
    path('api/messages/<int:id>/', ContactMessageDetailAPI.as_view(), name='api_message_detail'),
   path(
        "chat/",
        user_chat_room,
        name="chat_room",
    ),

    # Liste des conversations (admin)
    path(
        "admin/chat/",
        admin_chat_list,
        name="admin_chat_list",
    ),

    # Conversation spécifique (admin)
    path(
        "admin/chat/<int:conversation_id>/",
        admin_chat_room,
        name="admin_chat_room",
    ),
]