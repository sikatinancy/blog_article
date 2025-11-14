# users/api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from blog_articles.users.models import Profile
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re

# === 1. USER LIST ===
class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(source='profile.profile_image', read_only=True)
    birth_date = serializers.DateField(source='profile.birth_date', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'birth_date']

# === 2. JWT CUSTOM ===
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        return token

# === 3. SIGNUP ===
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    birth_date = serializers.DateField(required=True)
    profile_image = serializers.ImageField(required=False, allow_empty_file=True, allow_null=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'birth_date', 'profile_image')
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate_password(self, value):
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une lettre.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        profile_image = validated_data.pop('profile_image', None)
        birth_date = validated_data.pop('birth_date')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )

        # Le signal crée le profil → on le met à jour
        profile = user.profile
        profile.profile_image = profile_image
        profile.birth_date = birth_date
        profile.save()

        self.send_activation_email(user)
        return user

    def send_activation_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # SÉCURITÉ : fallback si FRONTEND_URL manquant
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://127.0.0.1:8000')
        activation_url = f"{frontend_url}/activate/{uid}/{token}/"

        subject = "Activez votre compte BlogApp"
        message = f"""
        Bonjour {user.username},

        Cliquez sur le lien pour activer votre compte :
        {activation_url}

        Cordialement,
        L'équipe BlogApp
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )