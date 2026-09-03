# blog_articles/newsletter/views/start.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Count
# BON
from blog_articles.newsletter.models import Subscriber

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def start_subscription(request):
    email = request.data.get('email', '').strip().lower()

    if not email or '@' not in email or '.' not in email:
        return Response({
            'success': False,
            'message': 'Veuillez entrer un email valide.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Crée ou récupère l'abonné
    subscriber, _ = Subscriber.objects.get_or_create(email=email)

    # Tous les utilisateurs ayant publié au moins 1 article
    authors = User.objects.filter(articles__isnull=False) \
        .annotate(article_count=Count('articles')) \
        .distinct() \
        .order_by('-article_count')

    serializer = AuthorSerializer(authors, many=True)

    return Response({
        'success': True,
        'authors': serializer.data
    })