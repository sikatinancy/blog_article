from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views import View
from django.shortcuts import redirect
from users.api.serializers import CustomTokenObtainPairSerializer

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)

        token_serializer = CustomTokenObtainPairSerializer(data={'username': username, 'password': password})
        if token_serializer.is_valid():
            return Response({
                'access_token': str(token_serializer.validated_data['access']),
                'refresh_token': str(token_serializer.validated_data['refresh']),
                'is_superuser': user.is_superuser
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)


class LoginPageView(TemplateView):
    template_name = 'users/login.html'

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('users:home')


