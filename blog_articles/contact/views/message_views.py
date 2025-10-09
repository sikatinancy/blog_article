from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from blog_articles.contact.models import ContactMessage
from blog_articles.contact.tasks import send_contact_email

class MessageCreateView(UserPassesTestMixin, TemplateView):
    template_name = 'contact/message_form.html'

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request):
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        try:
            ContactMessage.objects.create(
                user=self.request.user,
                subject=subject,
                message=message
            )
            send_contact_email.delay(subject, message, self.request.user.email, 'admin@blogapp.com')
            return redirect('users:admin_dashboard')
        except Exception as e:
            return render(request, self.template_name, {'error': str(e)})

class MessageEditView(UserPassesTestMixin, TemplateView):
    template_name = 'contact/message_form.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = ContactMessage.objects.get(id=self.kwargs['id'])
        return context

    def post(self, request, id):
        message = ContactMessage.objects.get(id=id)
        message.subject = request.POST.get('subject')
        message.message = request.POST.get('message')
        message.is_read = request.POST.get('is_read') == 'on'
        try:
            message.save()
            return redirect('users:admin_dashboard')
        except Exception as e:
            return render(request, self.template_name, {'error': str(e), 'message': message})

class MessageDeleteView(UserPassesTestMixin, TemplateView):
    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, id):
        try:
            ContactMessage.objects.get(id=id).delete()
            return redirect('users:admin_dashboard')
        except ContactMessage.DoesNotExist:
            return redirect('users:admin_dashboard')

class MessageDetailView(UserPassesTestMixin, TemplateView):
    template_name = 'contact/message_detail.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = ContactMessage.objects.get(id=self.kwargs['id'])
        message.is_read = True
        message.save()
        context['message'] = message
        return context

class MessageReplyView(UserPassesTestMixin, TemplateView):
    template_name = 'contact/message_reply.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = ContactMessage.objects.get(id=self.kwargs['id'])
        return context

    def post(self, request, id):
        message = ContactMessage.objects.get(id=id)
        reply = request.POST.get('reply')
        try:
            message.reply = reply
            message.save()
            send_contact_email.delay(
                f"Réponse à : {message.subject}",
                reply,
                'admin@blogapp.com',
                message.user.email if message.user else request.POST.get('email')
            )
            return redirect('users:admin_dashboard')
        except Exception as e:
            return render(request, self.template_name, {'error': str(e), 'message': message})