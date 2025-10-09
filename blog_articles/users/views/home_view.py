from django.views.generic import TemplateView
from django.contrib.auth.models import User
from blog_articles.blog.models import Article, Comment
from blog_articles.contact.models import ContactMessage

class HomeView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        print(f"Rendering template: {self.template_name}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(published=True)
        context['comments'] = Comment.objects.filter(published=True)
        context['article_count'] = Article.objects.filter(published=True).count()
        context['comment_count'] = Comment.objects.filter(published=True).count()
        context['user_count'] = User.objects.count()
        context['message_count'] = ContactMessage.objects.count()
        return context