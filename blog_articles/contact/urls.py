from django.urls import path
from contact.views.message_views import MessageCreateView, MessageEditView, MessageDeleteView, MessageDetailView, MessageReplyView
from contact.api.viewsets import ContactMessageListAPI, ContactMessageDetailAPI

app_name = 'contact'
urlpatterns = [
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:id>/edit/', MessageEditView.as_view(), name='message_edit'),
    path('messages/<int:id>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('messages/<int:id>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:id>/reply/', MessageReplyView.as_view(), name='message_reply'),
    path('api/messages/', ContactMessageListAPI.as_view(), name='message_list'),
    path('api/messages/<int:id>/', ContactMessageDetailAPI.as_view(), name='message_detail'),
]