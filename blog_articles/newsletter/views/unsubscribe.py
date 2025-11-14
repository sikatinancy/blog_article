# blog_articles/newsletter/views/unsubscribe.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Subscription

@api_view(['GET'])
@permission_classes([AllowAny])  # Autorise les requêtes anonymes
def unsubscribe(request):
    """
    Désabonne un utilisateur d'un auteur via lien email.
    """
    email = request.query_params.get('email', '').strip().lower()
    author_id = request.query_params.get('author')

    if not email or not author_id:
        return Response(
            {'success': False, 'message': 'Paramètres manquants (email ou author).'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        author_id = int(author_id)
    except ValueError:
        return Response(
            {'success': False, 'message': 'ID auteur invalide.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    deleted_count, _ = Subscription.objects.filter(
        subscriber__email=email,
        author_id=author_id
    ).delete()

    if deleted_count > 0:
        return Response({'success': True, 'message': 'Vous êtes désabonné avec succès.'})
    else:
        return Response({'success': False, 'message': 'Aucun abonnement trouvé.'})