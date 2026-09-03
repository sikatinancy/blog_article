from django.test import TestCase

# Create your tests here.
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from blog_articles.blog.models import Article, CartItem, Comment
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
        'price': '25.50',
        'published': 'on'
    })
    assert response.status_code == 302
    article = Article.objects.get(title='Test Article')
    assert article.price == 25.50

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


@pytest.mark.django_db
def test_article_detail_adds_and_removes_article_from_cart(client, user):
    article = Article.objects.create(
        title='Article panier',
        description='Description',
        author=user,
        published=True,
        price='10.00',
    )
    client.force_login(user)

    detail = client.get(reverse('blog:article_detail', kwargs={'id': article.id}))
    assert detail.status_code == 200
    assert 'Ajouter au panier' in detail.content.decode()

    response = client.post(reverse('blog:cart_add', kwargs={'id': article.id}), {
        'next': reverse('blog:article_detail', kwargs={'id': article.id}),
    })
    assert response.status_code == 302
    assert response.url == reverse('blog:article_detail', kwargs={'id': article.id})
    assert CartItem.objects.get(user=user, article=article).quantity == 1

    detail = client.get(reverse('blog:article_detail', kwargs={'id': article.id}))
    assert 'Retirer du panier' in detail.content.decode()
    assert 'Passer la commande' in detail.content.decode()

    cart_item = CartItem.objects.get(user=user, article=article)
    response = client.post(reverse('blog:cart_remove', kwargs={'id': cart_item.id}))
    assert response.status_code == 302
    assert not CartItem.objects.filter(user=user, article=article).exists()