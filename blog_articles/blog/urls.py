# blog/urls.py
from django.urls import path
from blog_articles.blog.views.article_views import (
    ArticleCreateView, ArticleEditView, ArticleDeleteView, ArticleDetailView
)
from blog_articles.blog.views.comment_views import (
    CommentCreateView, CommentEditView, CommentDeleteView, CommentDetailView
)
from blog_articles.blog.api.viewsets import (
    ArticleListAPI, ArticleDetailAPI, CommentListAPI, CommentDetailAPI
)
from blog_articles.blog.views.shop_views import (
    CartAddView, CartDecreaseView, CartRemoveView, CartView,
    CheckoutView, OrderStatusView, OrderSuccessView,
)

app_name = 'blog'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:id>/', CartAddView.as_view(), name='cart_add'),
    path('cart/decrease/<int:id>/', CartDecreaseView.as_view(), name='cart_decrease'),
    path('cart/remove/<int:id>/', CartRemoveView.as_view(), name='cart_remove'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/<int:id>/success/', OrderSuccessView.as_view(), name='order_success'),
    path('orders/<int:id>/<str:status>/', OrderStatusView.as_view(), name='order_status'),
    # ARTICLES CRUD (pages)
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:id>/edit/', ArticleEditView.as_view(), name='article_edit'),
    path('articles/<int:id>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
    path('articles/<int:id>/', ArticleDetailView.as_view(), name='article_detail'),

    # COMMENTS CRUD (pages)
    path('comments/create/', CommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:id>/edit/', CommentEditView.as_view(), name='comment_edit'),
    path('comments/<int:id>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('comments/<int:id>/', CommentDetailView.as_view(), name='comment_detail'),

    # API endpoints
    path('api/articles/', ArticleListAPI.as_view(), name='article_list_api'),
    path('api/articles/', ArticleListAPI.as_view(), name='article_list'),
    path('api/articles/<int:id>/', ArticleDetailAPI.as_view(), name='article_detail_api'),
    path('api/comments/', CommentListAPI.as_view(), name='comment_list_api'),
    path('api/comments/<int:id>/', CommentDetailAPI.as_view(), name='comment_detail_api'),
]
