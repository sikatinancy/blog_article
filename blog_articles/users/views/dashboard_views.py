from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from blog_articles.blog.models import Article, CartItem, Comment, Order

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(author=self.request.user)
        context['comments'] = Comment.objects.filter(author=self.request.user)
        context['article_count'] = context['articles'].count()
        context['comment_count'] = context['comments'].count()
        context['cart_items'] = CartItem.objects.filter(user=self.request.user).select_related('article')
        context['orders'] = Order.objects.filter(user=self.request.user).prefetch_related('items')
        return context