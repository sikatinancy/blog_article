# blog_articles/newsletter/views/confirm.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
# BON
from blog_articles.newsletter.models import Subscriber, Subscription

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_subscription(request):
    email = request.data.get('email', '').strip().lower()
    author_ids = request.data.get('authors', [])

    if not email:
        return Response({'success': False, 'message': 'Email requis.'}, status=400)
    if not author_ids or not isinstance(author_ids, list):
        return Response({'success': False, 'message': 'Veuillez sélectionner au moins un auteur.'}, status=400)

    subscriber = get_object_or_404(Subscriber, email=email)
    subscribed_names = []
    created_count = 0

    for author_id in author_ids:
        try:
            author = User.objects.get(id=author_id)
            sub, created = Subscription.objects.get_or_create(
                subscriber=subscriber,
                author=author
            )
            if created:
                created_count += 1
                name = author.get_full_name().strip() or author.username
                subscribed_names.append(name)
        except User.DoesNotExist:
            continue

    if created_count == 0:
        message = "Vous étiez déjà abonné à ces auteurs."
    else:
        message = f"Vous êtes maintenant abonné à : {', '.join(subscribed_names)} avec succès !"

    return Response({
        'success': True,
        'message': message
    })