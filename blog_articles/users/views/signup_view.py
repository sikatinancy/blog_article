from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import IntegrityError
from blog_articles.users.models import Profile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.api.serializers import SignupSerializer, CustomTokenObtainPairSerializer
import json

class SignupView(TemplateView, APIView):
    template_name = 'users/register.html'
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # 🔹 Cas API JSON
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            serializer = SignupSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                Profile.objects.create(user=user)
                return Response({
                    'message': 'Inscription réussie. Veuillez vous connecter.'
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Cas formulaire HTML classique
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        email = request.POST.get('email', '').strip()

        if not username or not password or not email:
            return render(request, self.template_name, {'error': "Tous les champs sont obligatoires."})

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            Profile.objects.create(user=user)
            return redirect(reverse('users:login'))
        except IntegrityError:
            return render(request, self.template_name, {'error': "Ce nom d'utilisateur existe déjà."})
        except Exception as e:
            return render(request, self.template_name, {'error': f"Inscription échouée : {str(e)}"})
