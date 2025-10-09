from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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
            send_contact_email.delay(
                serializer.data['subject'],
                serializer.data['message'],
                request.user.email if request.user.is_authenticated else 'anonyme@blogapp.com',
                'admin@blogapp.com'
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactMessageDetailAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        try:
            message = ContactMessage.objects.get(id=id)
            message.is_read = True
            message.save()
            serializer = ContactMessageSerializer(message)
            return Response(serializer.data)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        try:
            message = ContactMessage.objects.get(id=id)
            serializer = ContactMessageSerializer(message, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if 'reply' in request.data:
                    send_contact_email.delay(
                        f"Réponse à : {message.subject}",
                        request.data['reply'],
                        'admin@blogapp.com',
                        message.user.email if message.user else request.data.get('email', 'anonyme@blogapp.com')
                    )
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            message = ContactMessage.objects.get(id=id)
            message.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Message non trouvé'}, status=status.HTTP_404_NOT_FOUND)