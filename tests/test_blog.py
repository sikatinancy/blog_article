import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from blog_articles.blog.models import Article, Comment
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_article_list_api(user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(reverse('blog:article_list'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_article_create_view(client, user):
    client.force_login(user)
    response = client.post(reverse('blog:article_create'), {
        'title': 'Test Article',
        'description': 'Test Description',
        'published': 'on'
    })
    assert response.status_code == 302
    assert Article.objects.filter(title='Test Article').exists()

@pytest.mark.django_db
def test_comment_create_view(client, user):
    article = Article.objects.create(title='Test', description='Test', author=user)
    client.force_login(user)
    response = client.post(reverse('blog:comment_create'), {
        'article': article.id,
        'content': 'Test Comment',
        'published': 'on'
    })
    assert response.status_code == 302
    assert Comment.objects.filter(content='Test Comment').exists()