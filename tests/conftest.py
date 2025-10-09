import pytest
from django.contrib.auth.models import User
from blog_articles.users.tests.factories import UserFactory


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass', email='test@example.com')