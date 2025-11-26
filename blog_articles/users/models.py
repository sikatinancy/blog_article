# blog_articles/users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
import random


# =======================================================
#  MODEL OTP POUR ACTIVATION PAR CODE EMAIL/SMS
# =======================================================

class OTP(models.Model):
    VERIF_CHOICES = (
        ('email', 'Email'),
        ('phone', 'Phone'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    code = models.CharField(max_length=10, blank=True)
    verification_type = models.CharField(max_length=10, choices=VERIF_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Code OTP"
        verbose_name_plural = "Codes OTP"
        db_table = "users_otp"
        indexes = [
            models.Index(fields=['user', 'code']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"OTP {self.code} - {self.user.email}"

    def generate_otp(self, length=6, expiry_minutes=15):
        """Génère le code OTP + expiration"""
        self.code = ''.join(random.choices('0123456789', k=length))
        self.expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        self.save(update_fields=['code', 'expires_at'])
        return self.code

    def is_valid(self):
        """Vérifie si l'OTP est encore valide"""
        return self.code and timezone.now() <= self.expires_at


# =======================================================
#  PROFIL UTILISATEUR (EXISTANT)
# =======================================================

class Profile(models.Model):
    """
    Profil utilisateur étendu.
    Un profil est créé automatiquement à la création d'un User.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Utilisateur"
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        verbose_name="Photo de profil"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
        db_table = 'users_profile'

    def __str__(self):
        return f"{self.user.username}'s profile"


# =======================================================
#  SIGNALS PROFIL AUTOMATIQUE
# =======================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
