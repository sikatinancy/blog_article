from unittest.mock import patch

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from blog_articles.users.models import OTP, User
from blog_articles.users.utils import OTPEmailDeliveryError
from blog_articles.users.views.signup_view import issue_email_otp


pytestmark = pytest.mark.django_db


@pytest.fixture
def registration_data():
    return {
        "username": "nouvelutilisateur",
        "email": "new@example.com",
        "password": "motdepasse123",
        "password_confirm": "motdepasse123",
        "birth_date": "2000-01-01",
    }


def test_registration_sends_one_otp_email_and_creates_one_otp(registration_data):
    response = APIClient().post(reverse("users:register_api"), registration_data)

    assert response.status_code == 201
    user = User.objects.get(email=registration_data["email"])
    assert user.is_active is False
    assert OTP.objects.filter(user=user).count() == 1
    assert len(mail.outbox) == 1


def test_issue_email_otp_sets_expiration_and_code(registration_data):
    user = User.objects.create_user(
        username=registration_data["username"],
        email=registration_data["email"],
        password=registration_data["password"],
        is_active=False,
    )

    with patch("blog_articles.users.views.signup_view.send_otp_email") as send_mail_mock:
        issue_email_otp(user)

    otp = OTP.objects.get(user=user)
    assert otp.code
    assert otp.expires_at is not None
    assert otp.expires_at > timezone.now()
    send_mail_mock.assert_called_once_with(user.email, otp.code)


def test_registration_is_rolled_back_when_otp_email_fails(registration_data):
    with patch(
        "blog_articles.users.views.signup_view.send_otp_email",
        side_effect=OTPEmailDeliveryError("L'envoi du code de vérification a échoué."),
    ):
        response = APIClient().post(reverse("users:register_api"), registration_data)

    assert response.status_code == 503
    assert not User.objects.filter(email=registration_data["email"]).exists()
    assert OTP.objects.count() == 0
