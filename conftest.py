# blog_articles/conftest.py
import pytest
from blog_articles.blog.factories import UserFactory

@pytest.fixture
def user(db):
    return UserFactory()