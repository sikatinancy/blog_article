# blog_articles/contact/api/viewsets.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from blog_articles.contact.models import ContactMessage
from .serializers import ContactMessageSerializer
from blog_articles.contact.tasks import send_contact_email


class ContactMessageListAPI(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        messages = ContactMessage.objects.all()
        serializer = ContactMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(user=request.user if request.user.is_authenticated else None)
            user_email = message.get_recipient_email()  # Utilise ta méthode propre

            # E-mail à l'admin
            send_contact_email.delay(
                f"Nouveau message : {message.subject}",
                message.message,
                user_email,
                'admin@blogapp.com'
            )

            # Confirmation à l'utilisateur
            send_contact_email.delay(
                "Nous avons bien reçu votre message",
                f"Bonjour,\n\nMerci pour votre message intitulé « {message.subject} ».\n\n"
                f"Nous vous répondrons dans les plus brefs délais.\n\nCordialement,\nL'équipe du blog",
                'admin@blogapp.com',
                user_email
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactMessageDetailAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        message = get_object_or_404(ContactMessage, id=id)
        message.is_read = True
        message.save()
        serializer = ContactMessageSerializer(message)
        return Response(serializer.data)

    # MÉTHODE PUT CORRIGÉE ET FONCTIONNELLE
    def put(self, request, id):
        message = get_object_or_404(ContactMessage, id=id)
        serializer = ContactMessageSerializer(message, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Envoi de la réponse par e-mail si le champ "reply" est présent
            if 'reply' in request.data and request.data['reply'].strip():
                reply_text = request.data['reply']
                send_contact_email.delay(
                    f"Re: {message.subject}",
                    reply_text + "\n\n--\nCordialement,\nL'équipe du blog",
                    'admin@blogapp.com',
                    message.get_recipient_email()  # Utilise ta méthode sécurisée
                )

            return Response({
                "success": True,
                "message": "Réponse enregistrée et envoyée par e-mail !"
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        message = get_object_or_404(ContactMessage, id=id)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)