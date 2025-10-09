from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from blog_articles.blog.models import Article
from django.contrib import messages

class ArticleCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/article_form.html'

    def post(self, request):
        title = request.POST.get('title')
        description = request.POST.get('description')
        content = request.POST.get('content')
        category = request.POST.get('category')
        published = request.POST.get('published') == 'on'
        image = request.FILES.get('image')
        try:
            Article.objects.create(
                title=title,
                description=description,
                content=content,
                category=category,
                image=image,
                author=request.user,
                published=published
            )
            messages.success(request, 'Article créé avec succès.')
            return redirect('users:dashboard')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
            return render(request, self.template_name, {'error': str(e)})

class ArticleEditView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/article_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = Article.objects.get(id=self.kwargs['id'], author=self.request.user)
        return context

    def post(self, request, id):
        article = Article.objects.get(id=id, author=request.user)
        article.title = request.POST.get('title')
        article.description = request.POST.get('description')
        article.content = request.POST.get('content')
        article.category = request.POST.get('category')
        article.published = request.POST.get('published') == 'on'
        if request.FILES.get('image'):
            article.image = request.FILES.get('image')
        try:
            article.save()
            messages.success(request, 'Article modifié avec succès.')
            return redirect('users:dashboard')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
            return render(request, self.template_name, {'error': str(e), 'article': article})

class ArticleDeleteView(LoginRequiredMixin, TemplateView):
    def post(self, request, id):
        try:
            Article.objects.get(id=id, author=request.user).delete()
            messages.success(request, 'Article supprimé avec succès.')
            return redirect('users:dashboard')
        except Article.DoesNotExist:
            messages.error(request, 'Article introuvable.')
            return redirect('users:dashboard')

class ArticleDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = Article.objects.get(id=self.kwargs['id'], author=self.request.user)
        return context