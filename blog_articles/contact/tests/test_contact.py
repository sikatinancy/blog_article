import pytest
from django.urls import reverse
from blog_articles.contact.models import ContactMessage
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_contact_view(client):
    response = client.post(reverse('users:contact'), {
        'subject': 'Test',
        'message': 'Message test',
        'email': 'test@example.com'
    })
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 1

@pytest.mark.django_db
def test_message_create_view(client, user):
    user.is_superuser = True
    user.save()
    client.force_login(user)
    response = client.post(reverse('contact:message_create'), {
        'subject': 'Admin Message',
        'message': 'Message from admin'
    })
    assert response.status_code == 302
    assert ContactMessage.objects.filter(subject='Admin Message').exists()