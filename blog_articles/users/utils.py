# users/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_otp_email(to_email: str, code: str):
    subject = "Votre code de vérification"
    html_message = render_to_string('users/otp_email.html', {'code': code})
    send_mail(
        subject=subject,
        message=f"Votre code OTP: {code}",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        recipient_list=[to_email],
        html_message=html_message,
        fail_silently=False
    )

def send_otp_phone(phone_number: str, code: str):
    # Placeholder : intégrer provider SMS / WhatsApp (Twilio, Africa's Talking, etc.)
    # Ici on renvoie simplement True pour tests locaux
    print(f"[SMS] Envoyer OTP {code} vers {phone_number}")
    return True
