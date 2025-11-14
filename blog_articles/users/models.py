# blog_articles/users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


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
        db_table = 'users_profile'  # Optionnel : force le nom de table

    def __str__(self):
        return f"{self.user.username}'s profile"


# === SIGNAL : CRÉER LE PROFIL AUTOMATIQUEMENT ===
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée un profil vide dès qu'un utilisateur est créé.
    """
    if created:
        Profile.objects.get_or_create(user=instance)


# === SIGNAL : SAUVEGARDER LE PROFIL LORSQUE L'UTILISATEUR EST MODIFIÉ ===
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Sauvegarde le profil associé si des champs sont modifiés via l'utilisateur.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()