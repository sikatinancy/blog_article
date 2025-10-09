from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_contact_email(subject, message, from_email, to_email):
    send_mail(
        subject,
        message,
        from_email,
        [to_email],
        fail_silently=False,
    )