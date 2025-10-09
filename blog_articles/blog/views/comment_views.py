from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from blog_articles.blog.models import Comment, Article
from django.contrib import messages

class CommentCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/comment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(author=self.request.user)
        return context

    def post(self, request):
        article_id = request.POST.get('article')
        content = request.POST.get('content')
        published = request.POST.get('published') == 'on'
        try:
            article = Article.objects.get(id=article_id, author=request.user)
            Comment.objects.create(
                article=article,
                content=content,
                author=request.user,
                published=published
            )
            messages.success(request, 'Commentaire créé avec succès.')
            return redirect('users:dashboard')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
            return render(request, self.template_name, {'error': str(e), 'articles': Article.objects.filter(author=request.user)})

class CommentEditView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/comment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = Comment.objects.get(id=self.kwargs['id'], author=self.request.user)
        context['articles'] = Article.objects.filter(author=self.request.user)
        return context

    def post(self, request, id):
        comment = Comment.objects.get(id=id, author=self.request.user)
        comment.article = Article.objects.get(id=request.POST.get('article'), author=request.user)
        comment.content = request.POST.get('content')
        comment.published = request.POST.get('published') == 'on'
        try:
            comment.save()
            messages.success(request, 'Commentaire modifié avec succès.')
            return redirect('users:dashboard')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
            return render(request, self.template_name, {'error': str(e), 'comment': comment, 'articles': Article.objects.filter(author=self.request.user)})

class CommentDeleteView(LoginRequiredMixin, TemplateView):
    def post(self, request, id):
        try:
            Comment.objects.get(id=id, author=self.request.user).delete()
            messages.success(request, 'Commentaire supprimé avec succès.')
            return redirect('users:dashboard')
        except Comment.DoesNotExist:
            messages.error(request, 'Commentaire introuvable.')
            return redirect('users:dashboard')

class CommentDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/comment_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = Comment.objects.get(id=self.kwargs['id'], author=self.request.user)
        return context