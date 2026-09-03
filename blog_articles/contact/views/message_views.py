# blog_articles/contact/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
# CORRECT
from blog_articles.contact.models import ContactMessage
# BON
from blog_articles.contact.api.serializers import ContactMessageSerializer
# BON
from blog_articles.contact.tasks import send_contact_email


# ===================== API =====================
class ContactMessageListAPI(APIView):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request):
        messages = ContactMessage.objects.all()
        serializer = ContactMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(
                user=request.user if request.user.is_authenticated else None
            )
            user_email = message.get_recipient_email()

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
                f"Bonjour,\n\nMerci pour votre message :\n\n« {message.subject} »\n\n"
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

    def put(self, request, id):
        message = get_object_or_404(ContactMessage, id=id)
        serializer = ContactMessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            if 'reply' in request.data and request.data['reply'].strip():
                send_contact_email.delay(
                    f"Re: {message.subject}",
                    request.data['reply'] + "\n\n--\nCordialement,\nL'équipe du blog",
                    'admin@blogapp.com',
                    message.get_recipient_email()
                )

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        message = get_object_or_404(ContactMessage, id=id)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===================== VUES CLASSIQUES (TOUT CONSERVÉ) =====================
class MessageCreateView(UserPassesTestMixin, TemplateView):
    template_name = 'contact/message_form.html'
    def test_func(self): return self.request.user.is_superuser

    def post(self, request):
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        try:
            ContactMessage.objects.create(
                user=request.user,
                subject=subject,
                message=message_text
            )
            return redirect('users:admin_dashboard')
        except Exception as e:
            return render(request, self.template_name, {'error': str(e)})


class MessageEditView(UserPassesTestMixin, TemplateView):
    template_name = 'contact/message_form.html'
    def test_func(self): return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = get_object_or_404(ContactMessage, id=self.kwargs['id'])
        return context

    def post(self, request, id):
        message = get_object_or_404(ContactMessage, id=id)
        message.subject = request.POST.get('subject', message.subject)
        message.message = request.POST.get('message', message.message)
        message.is_read = request.POST.get('is_read') == 'on'
        message.save()
        return redirect('users:admin_dashboard')


class MessageDeleteView(UserPassesTestMixin, TemplateView):
    def test_func(self): return self.request.user.is_superuser

    def post(self, request, id):
        get_object_or_404(ContactMessage, id=id).delete()
        return redirect('users:admin_dashboard')


class MessageDetailView(UserPassesTestMixin, TemplateView):
    template_name = 'contact/message_detail.html'
    def test_func(self): return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = get_object_or_404(ContactMessage, id=self.kwargs['id'])
        if not message.is_read:
            message.is_read = True
            message.save()
        context['message'] = message
        return context


class MessageReplyView(UserPassesTestMixin, TemplateView):
    template_name = 'contact/message_reply.html'
    def test_func(self): return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = get_object_or_404(ContactMessage, id=self.kwargs['id'])
        return context