# users/views/auth_views.py
from django.views.generic import TemplateView, View
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from blog_articles.users.api.serializers import OTPVerifySerializer

# CustomTokenObtainPairSerializer dépend de ton implémentation JWT, je le laisse inchangé
from blog_articles.users.api.serializers import CustomTokenObtainPairSerializer

User = get_user_model()

# Page login
class LoginPageView(TemplateView):
    template_name = 'users/login.html'


# API login
class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email et mot de passe requis.'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Identifiants invalides.'}, status=401)

        if not user.is_active:
            return Response({
                'error': 'Compte non activé. Veuillez vérifier votre email et valider l’OTP.'
            }, status=401)

        authenticated_user = authenticate(request, username=user.username if hasattr(user, 'username') else user.email, password=password)
        if not authenticated_user:
            return Response({'error': 'Mot de passe incorrect.'}, status=401)

        login(request, authenticated_user)

        token_serializer = CustomTokenObtainPairSerializer()
        token = token_serializer.get_token(authenticated_user)

        return Response({
            'access_token': str(token.access_token),
            'refresh_token': str(token),
            'is_superuser': authenticated_user.is_superuser,
            'username': authenticated_user.username,
        }, status=200)


# Logout
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Déconnexion réussie.")
        return redirect('users:home')
