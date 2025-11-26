# users/views/signup_view.py
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from blog_articles.users.api.serializers import SignupSerializer, OTPVerifySerializer
from blog_articles.users.models import OTP
from blog_articles.users.utils import send_otp_email, send_otp_phone

User = get_user_model()


class SignupPageView(TemplateView):
    template_name = 'users/register.html'


class SignupAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Vérification unicité email / phone
            if User.objects.filter(email=data['email']).exists():
                return Response({'error': 'Cet email est déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)
            if data.get('phone') and User.objects.filter(phone=data['phone']).exists():
                return Response({'error': 'Ce numéro est déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)

            # Création utilisateur inactif
            user = serializer.save()

            # Type de vérification (email par défaut)
            verification_type = data.get('verification_type', 'email').lower()

            # Création OTP
            otp = OTP.objects.create(
                user=user,
                verification_type=verification_type,
                expires_at=timezone.now() + timedelta(minutes=15)
            )
            code = otp.generate_otp(length=6, expiry_minutes=15)

            # Envoi OTP
            if verification_type == 'email':
                send_otp_email(user.email, code)
            else:
                send_otp_phone(user.phone, code)

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

        identifier = serializer.validated_data['identifier']
        code = serializer.validated_data['code']

        # Recherche user par email ou phone
        user = User.objects.filter(email=identifier).first() or User.objects.filter(phone=identifier).first()
        if not user:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        # Trouver OTP valide
        otp_qs = OTP.objects.filter(user=user, code=code).order_by('-created_at')
        otp = otp_qs.first()

        if not otp:
            return Response({'error': 'Code OTP invalide'}, status=status.HTTP_400_BAD_REQUEST)

        if not otp.is_valid():
            # Code expiré → on en génère un nouveau automatiquement
            new_otp = OTP.objects.create(
                user=user,
                verification_type=otp.verification_type,
                expires_at=timezone.now() + timedelta(minutes=15)
            )
            new_code = new_otp.generate_otp(length=6, expiry_minutes=15)

            if new_otp.verification_type == 'email':
                send_otp_email(user.email, new_code)
            else:
                send_otp_phone(user.phone, new_code)

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