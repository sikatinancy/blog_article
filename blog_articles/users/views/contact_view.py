from django.views.generic import TemplateView
from django.shortcuts import render
from blog_articles.contact.models import ContactMessage
from blog_articles.contact.tasks import send_contact_email

class ContactView(TemplateView):
    template_name = 'contact/contact.html'

    def post(self, request):
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        from_email = request.user.email if request.user.is_authenticated else request.POST.get('email')
        ContactMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            subject=subject,
            message=message
        )
        send_contact_email.delay(subject, message, from_email, 'admin@blogapp.com')
        return render(request, self.template_name, {'success': 'Message envoyé !'})