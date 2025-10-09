from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from users.api.serializers import CustomTokenObtainPairSerializer

class LoginAPIView(APIView):
    # Désactiver l'authentification et les permissions pour cet endpoint
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            token_serializer = CustomTokenObtainPairSerializer(data={'username': username, 'password': password})
            if token_serializer.is_valid():
                return Response({
                    'access_token': str(token_serializer.validated_data['access']),
                    'refresh_token': str(token_serializer.validated_data['refresh']),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)