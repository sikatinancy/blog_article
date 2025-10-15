# blog/urls.py
from django.urls import path
from blog.views.article_views import (
    ArticleCreateView, ArticleEditView, ArticleDeleteView, ArticleDetailView
)
from blog.views.comment_views import (
    CommentCreateView, CommentEditView, CommentDeleteView, CommentDetailView
)
from blog.api.viewsets import (
    ArticleListAPI, ArticleDetailAPI, CommentListAPI, CommentDetailAPI
)

app_name = 'blog'

urlpatterns = [
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
    path('api/articles/<int:id>/', ArticleDetailAPI.as_view(), name='article_detail_api'),
    path('api/comments/', CommentListAPI.as_view(), name='comment_list_api'),
    path('api/comments/<int:id>/', CommentDetailAPI.as_view(), name='comment_detail_api'),
]
