from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from blog_articles.blog.models import Article, Comment
from blog_articles.contact.models import ContactMessage

class AdminDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'users/admin_super.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['articles'] = Article.objects.all()
        context['comments'] = Comment.objects.all()
        context['messages'] = ContactMessage.objects.all()
        context['user_count'] = User.objects.count()
        context['article_count'] = Article.objects.count()
        context['comment_count'] = Comment.objects.count()
        context['message_count'] = ContactMessage.objects.count()
        return context