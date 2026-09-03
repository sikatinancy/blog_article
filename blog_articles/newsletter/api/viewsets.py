# blog_articles/newsletter/api/viewsets.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count

# BON
from blog_articles.newsletter.models import Subscriber, Subscription
from .serializers import AuthorSerializer

User = get_user_model()


class NewsletterAPI(viewsets.ViewSet):
    """
    API complète pour le système de newsletter (abonnement par email)
    Utilisé via /newsletter/start/, /newsletter/confirm/, etc.
    """

    @action(detail=False, methods=['post'], url_path='start')
    def start(self, request):
        """
        Étape 1 : Enregistrer l'email → renvoyer la liste des auteurs ayant publié
        """
        email = request.data.get('email', '').strip().lower()

        if not email or '@' not in email or '.' not in email:
            return Response({
                'success': False,
                'message': 'Veuillez entrer un email valide.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Crée ou récupère l'abonné
        Subscriber.objects.get_or_create(email=email)

        # Tous les auteurs (User) ayant au moins un article
        authors = User.objects.filter(articles__isnull=False) \
            .annotate(article_count=Count('articles')) \
            .distinct() \
            .order_by('-article_count')

        serializer = AuthorSerializer(authors, many=True)

        return Response({
            'success': True,
            'authors': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm(self, request):
        """
        Étape 2 : Confirmer l'abonnement aux auteurs sélectionnés
        """
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
                author = User.objects.get(id=int(author_id))
                subscription, created = Subscription.objects.get_or_create(
                    subscriber=subscriber,
                    author=author
                )
                if created:
                    created_count += 1
                    name = (author.get_full_name() or author.username).strip()
                    if name:
                        subscribed_names.append(name)
            except (User.DoesNotExist, ValueError):
                continue

        if created_count == 0:
            message = "Vous étiez déjà abonné à ces auteurs."
        else:
            authors_list = ', '.join(subscribed_names)
            message = f"Vous êtes maintenant abonné à : {authors_list} avec succès !"

        return Response({
            'success': True,
            'message': message
        })

    @action(detail=False, methods=['get'], url_path='unsubscribe')
    def unsubscribe(self, request):
        """
        Désabonnement via lien dans l'email
        """
        email = request.query_params.get('email', '').strip().lower()
        author_id = request.query_params.get('author')

        if not email or not author_id:
            return Response({
                'success': False,
                'message': 'Paramètres manquants (email ou author).'
            }, status=400)

        try:
            author_id = int(author_id)
        except ValueError:
            return Response({'success': False, 'message': 'ID auteur invalide.'}, status=400)

        deleted_count, _ = Subscription.objects.filter(
            subscriber__email=email,
            author_id=author_id
        ).delete()

        if deleted_count > 0:
            return Response({'success': True, 'message': 'Vous avez été désabonné avec succès.'})
        else:
            return Response({'success': False, 'message': 'Aucun abonnement trouvé.'})