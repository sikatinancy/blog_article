# blog_articles/newsletter/api/viewsets.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from ..models import Author, Subscriber, Subscription
from .serializers import AuthorSerializer

class NewsletterAPI(viewsets.ViewSet):

    @action(detail=False, methods=['post'], url_path='start')
    def start(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email or '@' not in email:
            return Response({'success': False, 'message': 'Email invalide'}, status=status.HTTP_400_BAD_REQUEST)
        Subscriber.objects.get_or_create(email=email)
        authors = Author.objects.annotate(article_count=Count('articles')).order_by('-article_count')
        serializer = AuthorSerializer(authors, many=True)
        return Response({'success': True, 'authors': serializer.data})

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm(self, request):
        email = request.data.get('email')
        author_ids = request.data.get('authors', [])
        if not email or not author_ids:
            return Response({'success': False, 'message': 'Données manquantes'}, status=status.HTTP_400_BAD_REQUEST)
        subscriber = get_object_or_404(Subscriber, email=email)
        created_count = 0
        for author_id in author_ids:
            author = get_object_or_404(Author, id=author_id)
            _, created = Subscription.objects.get_or_create(subscriber=subscriber, author=author)
            if created:
                created_count += 1
        return Response({
            'success': True,
            'message': f'Abonnement confirmé ! (+{created_count})'
        })

    @action(detail=False, methods=['get'], url_path='unsubscribe')
    def unsubscribe(self, request):
        email = request.query_params.get('email')
        author_id = request.query_params.get('author')
        if not email or not author_id:
            return Response({'success': False, 'message': 'Paramètres manquants'}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = Subscription.objects.filter(
            subscriber__email=email,
            author_id=author_id
        ).delete()
        if deleted_count > 0:
            return Response({'success': True, 'message': 'Désabonné avec succès.'})
        return Response({'success': False, 'message': 'Aucun abonnement trouvé.'})