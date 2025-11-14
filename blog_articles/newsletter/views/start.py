# blog_articles/newsletter/views/start.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from ..models import Author, Subscriber
from ..api.serializers import AuthorSerializer

@api_view(['POST'])
@permission_classes([AllowAny])  # Autorise les requêtes anonymes
def start_subscription(request):
    """
    Étape 1 : Enregistre l'email et renvoie la liste des auteurs triés par nombre d'articles.
    """
    email = request.data.get('email', '').strip().lower()

    if not email or '@' not in email:
        return Response(
            {'success': False, 'message': 'Veuillez entrer un email valide.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Crée ou récupère l'abonné
    subscriber, created = Subscriber.objects.get_or_create(email=email)
    if created:
        subscriber.subscribed_at = subscriber.subscribed_at  # auto_now_add
        subscriber.save()

    # Récupère les auteurs triés par nombre d'articles
    authors = Author.objects.annotate(
        article_count=Count('articles')
    ).order_by('-article_count').values('id', 'name', 'article_count')

    serializer = AuthorSerializer(authors, many=True)
    return Response({'success': True, 'authors': serializer.data})