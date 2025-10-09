import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_login_view(client, user):
    response = client.post(reverse('users:login'), {'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 302

@pytest.mark.django_db
def test_register_view(client):
    response = client.post(reverse('users:register'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass'
    })
    assert response.status_code == 302

@pytest.mark.django_db
def test_user_create_view(client, user):
    client.force_login(user)
    user.is_superuser = True
    user.save()
    response = client.post(reverse('users:user_create'), {
        'username': 'newadmin',
        'email': 'newadmin@example.com',
        'password': 'newpass'
    })
    assert response.status_code == 302
    assert User.objects.filter(username='newadmin').exists()