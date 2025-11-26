# users/api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from blog_articles.users.models import Profile, OTP
from blog_articles.users.utils import send_otp_email
from django.utils import timezone
import re


# ======================================================
#     1. USER LIST
# ======================================================

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(source='profile.profile_image', read_only=True)
    birth_date = serializers.DateField(source='profile.birth_date', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'birth_date']


# ======================================================
#     2. CUSTOM JWT
# ======================================================

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        return token


# ======================================================
#     3. SIGNUP AVEC OTP (NOUVELLE VERSION)
# ======================================================

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    birth_date = serializers.DateField(required=True)
    profile_image = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)

    # IMPORTANT : L'utilisateur choisit le mode
    verification_type = serializers.ChoiceField(
        choices=[('email', 'email')],
        default='email'
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'birth_date', 'profile_image', 'verification_type'
        )
        extra_kwargs = {'email': {'required': True}}

    # ------------------------ VALIDATIONS ------------------------

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
        """Vérification des deux mots de passe"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        return data

    # ------------------------ CREATION UTILISATEUR + OTP ------------------------

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        profile_image = validated_data.pop('profile_image', None)
        birth_date = validated_data.pop('birth_date')
        verification_type = validated_data.pop('verification_type')

        # Création du compte inactif
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )

        # Mise à jour du profil créé automatiquement par signal
        profile = user.profile
        profile.profile_image = profile_image
        profile.birth_date = birth_date
        profile.save()

        # ------------------- CREATION OTP -------------------
        otp = OTP.objects.create(
            user=user,
            verification_type=verification_type,
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        code = otp.generate_otp()

        # ------------------- ENVOI EMAIL -------------------
        send_otp_email(user.email, code)

        return user


# ======================================================
#     4. VERIFICATION OTP
# ======================================================

class OTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField()
    code = serializers.CharField()
