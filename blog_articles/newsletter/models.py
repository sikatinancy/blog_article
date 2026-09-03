# blog_articles/newsletter/models.py
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context
from django.contrib.auth import get_user_model

User = get_user_model()

class Article(models.Model):
    title = models.CharField("Titre", max_length=255)
    content = models.TextField("Contenu")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name="Auteur"
    )
    published_at = models.DateTimeField("Publié le", auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):   # ← CORRIGÉ ICI
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.send_notification()

    def send_notification(self):
        # ... ton code d'envoi d'email reste inchangé
        subscriber_emails = self.author.subscribers.values_list('subscriber__email', flat=True)
        if not subscriber_emails:
            return

        subject = f"Nouvelle publication : {self.title}"
        article_url = f"{settings.SITE_URL}/blog/article/{self.id}/"

        html_template = """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #1f2937;">{{ title }}</h2>
            <p style="color: #6b7280;">Par <strong>{{ author_name }}</strong></p>
            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="color: #374151;">{{ content_snippet }}...</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{ article_url }}" style="background: #3b82f6; color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Lire l'article complet
                </a>
            </div>
            <p style="font-size: 12px; color: #9ca3af; text-align: center;">
                Vous recevez cet email car vous êtes abonné(e) à {{ author_name }}.<br>
                <a href="{{ unsubscribe_url }}" style="color: #9ca3af;">Se désabonner de cet auteur</a>
            </p>
        </div>
        """

        template = Template(html_template)

        for email in subscriber_emails_:
            unsubscribe_url = f"{settings.SITE_URL}/newsletter/unsubscribe/?email={email}&author={self.author.id}"
            context = Context({
                'title': self.title,
                'author_name': self.author.get_full_name() or self.author.username,
                'content_snippet': self.content[:200],
                'article_url': article_url,
                'unsubscribe_url': unsubscribe_url,
            })
            html_message = template.render(context)

            send_mail(
                subject=subject,
                message=html_message[:500] + "...",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )


class Subscriber(models.Model):
    email = models.EmailField("Email", unique=True)
    subscribed_at = models.DateTimeField("Inscrit le", auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Abonné"
        verbose_name_plural = "Abonnés"


class Subscription(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField("Abonné le", auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'author')
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"

    def __str__(self):
        return f"{self.subscriber.email} → {self.author.username}"