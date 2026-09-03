# users/views/signup_view.py
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from blog_articles.users.api.serializers import SignupSerializer, OTPVerifySerializer
from blog_articles.users.models import OTP
from blog_articles.users.utils import OTPEmailDeliveryError, send_otp_email

User = get_user_model()


def issue_email_otp(user):
    """Remplace les anciens codes par un unique code utilisable pendant 15 min."""
    OTP.objects.filter(user=user, verification_type="email").delete()
    otp = OTP(user=user, verification_type="email")
    code = otp.generate_otp(length=6, expiry_minutes=15)
    send_otp_email(user.email, code)


class SignupPageView(TemplateView):
    template_name = 'users/register.html'


class SignupAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        # Un compte créé lors d'un incident SMTP peut demander un nouveau code.
        email = request.data.get("email", "").strip().lower()
        existing_user = User.objects.filter(email__iexact=email, is_active=False).first()
        if existing_user:
            try:
                with transaction.atomic():
                    issue_email_otp(existing_user)
            except OTPEmailDeliveryError as exc:
                return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            return Response({
                "success": True,
                "message": "Un nouveau code OTP a été envoyé.",
                "redirect_to": f"/users/verify-otp/?identifier={existing_user.email}",
            })

        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            try:
                # Si SMTP échoue, toute l'inscription est annulée : aucun compte bloqué.
                with transaction.atomic():
                    user = serializer.save()
                    issue_email_otp(user)
            except OTPEmailDeliveryError as exc:
                return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # REDIRECTION DIRECTE VERS LA PAGE OTP AVEC EMAIL PRÉ-REMPLI
            return Response({
                'success': True,
                'message': 'Inscription réussie ! Un code OTP a été envoyé.',
                'redirect_to': f'/users/verify-otp/?identifier={user.email}'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        identifier = serializer.validated_data['identifier'].strip().lower()
        code = serializer.validated_data['code'].strip()

        # Recherche user par email ou phone
        user = User.objects.filter(email=identifier).first() or User.objects.filter(phone=identifier).first()
        if not user:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        # Trouver OTP valide
        otp_qs = OTP.objects.filter(
            user=user,
            verification_type='email',
            code=code,
        ).order_by('-created_at')
        otp = otp_qs.first()

        if not otp:
            return Response({'error': 'Code OTP invalide'}, status=status.HTTP_400_BAD_REQUEST)

        if not otp.is_valid():
            # Code expiré → on en génère un nouveau automatiquement
            try:
                with transaction.atomic():
                    issue_email_otp(user)
            except OTPEmailDeliveryError as exc:
                return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            return Response({
                'error': 'Code expiré. Un nouveau code a été envoyé.',
                'redirect_to': f'/users/verify-otp/?identifier={user.email}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Tout est bon → activation
        user.is_active = True
        user.save()

        # Nettoyage des anciens OTP
        OTP.objects.filter(user=user).delete()

        return Response({
            'success': True,
            'message': 'Compte activé avec succès ! Vous pouvez maintenant vous connecter.',
            'redirect_to': '/users/login/'
        }, status=status.HTTP_200_OK)
