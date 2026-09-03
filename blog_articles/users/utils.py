# users/utils.py
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)


class OTPEmailDeliveryError(Exception):
    """L'e-mail OTP n'a pas pu être remis par le fournisseur configuré."""


def _validate_email_configuration():
    """Évite de créer des comptes bloqués avec une configuration SMTP factice."""
    if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
        return

    missing = [
        name for name in ("EMAIL_HOST", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD")
        if not getattr(settings, name, "")
    ]
    password = getattr(settings, "EMAIL_HOST_PASSWORD", "")
    if missing or password.startswith("<") or "MOT_DE_PASSE" in password.upper():
        raise OTPEmailDeliveryError(
            "Le service d'envoi d'e-mails n'est pas configuré. "
            "Renseignez un mot de passe d'application Gmail valide."
        )

def send_otp_email(to_email: str, code: str):
    _validate_email_configuration()
    try:
        html_message = render_to_string("users/otp_email.html", {"code": code})
        sent = send_mail(
            subject="Votre code de vérification",
            message=f"Votre code OTP: {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as exc:
        logger.exception("Échec de l'envoi de l'OTP à %s", to_email)
        raise OTPEmailDeliveryError("L'envoi du code de vérification a échoué.") from exc

    if sent != 1:
        raise OTPEmailDeliveryError("L'envoi du code de vérification a échoué.")

def send_otp_phone(phone_number: str, code: str):
    # Placeholder : intégrer provider SMS / WhatsApp (Twilio, Africa's Talking, etc.)
    # Ici on renvoie simplement True pour tests locaux
    print(f"[SMS] Envoyer OTP {code} vers {phone_number}")
    return True
