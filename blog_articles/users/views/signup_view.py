from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from blog_articles.users.models import Profile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.api.serializers import SignupSerializer, CustomTokenObtainPairSerializer

class SignupView(TemplateView, APIView):
    template_name = 'users/register.html'

    # Désactiver l'authentification et les permissions pour toutes les requêtes
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        # Rendre le formulaire HTML pour toutes les requêtes GET
        return self.render_to_response({})

    def post(self, request):
        # Vérifier si la requête est pour l'API (Content-Type: application/json)
        if request.content_type == 'application/json':
            serializer = SignupSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                Profile.objects.create(user=user)
                token_serializer = CustomTokenObtainPairSerializer()
                token = token_serializer.get_token(user)
                return Response({
                    'user': SignupSerializer(user).data,
                    'token': {
                        'access': str(token.access_token),
                        'refresh': str(token),
                    }
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Logique pour le formulaire HTML
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            Profile.objects.create(user=user)
            return redirect('users:login')
        except Exception as e:
            return render(request, self.template_name, {'error': f'Inscription échouée : {str(e)}'})