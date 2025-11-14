# blog_articles/newsletter/views/confirm.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Subscriber, Subscription, Author

@api_view(['POST'])
@permission_classes([AllowAny])  # Autorise les requêtes anonymes
def confirm_subscription(request):
    """
    Étape 2 : Confirme l'abonnement aux auteurs sélectionnés.
    """
    email = request.data.get('email', '').strip().lower()
    author_ids = request.data.get('authors', [])

    if not email:
        return Response(
            {'success': False, 'message': 'Email manquant.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not author_ids or not isinstance(author_ids, list):
        return Response(
            {'success': False, 'message': 'Sélectionnez au moins un auteur.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    subscriber = get_object_or_404(Subscriber, email=email)
    created_count = 0

    for author_id in author_ids:
        author = get_object_or_404(Author, id=author_id)
        subscription, created = Subscription.objects.get_or_create(
            subscriber=subscriber,
            author=author
        )
        if created:
            created_count += 1

    return Response({
        'success': True,
        'message': f'Abonnement confirmé ! (+{created_count} auteur{"s" if created_count > 1 else ""})'
    })