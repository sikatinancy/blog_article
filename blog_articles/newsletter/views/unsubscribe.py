# blog_articles/newsletter/views/unsubscribe.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# BON
from blog_articles.newsletter.models import Subscriber, Subscription

@api_view(['GET'])
@permission_classes([AllowAny])
def unsubscribe(request):
    email = request.query_params.get('email', '').strip().lower()
    author_id = request.query_params.get('author')

    if not email or not author_id:
        return Response({'success': False, 'message': 'Paramètres manquants.'}, status=400)

    try:
        author_id = int(author_id)
    except ValueError:
        return Response({'success': False, 'message': 'ID invalide.'}, status=400)

    deleted, _ = Subscription.objects.filter(
        subscriber__email=email,
        author_id=author_id
    ).delete()

    if deleted:
        return Response({'success': True, 'message': 'Vous avez été désabonné avec succès.'})
    else:
        return Response({'success': False, 'message': 'Aucun abonnement trouvé.'})