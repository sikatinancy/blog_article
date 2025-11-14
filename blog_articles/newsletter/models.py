# blog_articles/newsletter/models.py
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

    @property
    def article_count(self):
        return self.articles.count()

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='articles')
    published_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.send_notification()

    def send_notification(self):
        subscribers = self.author.subscribers.values_list('subscriber__email', flat=True)
        if not subscribers:
            return

        subject = f"Nouvelle publication : {self.title}"
        url = f"{settings.SITE_URL}/blog/article/{self.id}/"

        message_template = """
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">
            <h2 style="color:#1f2937;">{{ title }}</h2>
            <p style="color:#6b7280;">Par <strong>{{ author_name }}</strong></p>
            <hr style="border:1px solid #e5e7eb;margin:20px 0;">
            <p style="color:#374151;">{{ content_snippet }}...</p>
            <div style="text-align:center;margin:30px 0;">
                <a href="{{ article_url }}" style="background:#3b82f6;color:white;padding:12px 24px;text-decoration:none;border-radius:8px;font-weight:bold;">
                    Lire l'article
                </a>
            </div>
            <p style="font-size:12px;color:#9ca3af;text-align:center;">
                <a href="{{ unsubscribe_url }}" style="color:#9ca3af;">
                    Se désabonner
                </a>
            </p>
        </div>
        """

        template = Template(message_template)

        for sub_email in subscribers:
            unsubscribe_url = f"{settings.SITE_URL}/newsletter/unsubscribe/?email={sub_email}&author={self.author.id}"
            context = Context({
                'title': self.title,
                'author_name': self.author.name,
                'content_snippet': self.content[:200],
                'article_url': url,
                'unsubscribe_url': unsubscribe_url,
            })
            rendered_message = template.render(context)
            send_mail(
                subject,
                rendered_message,  # Plain text fallback (could strip HTML)
                settings.DEFAULT_FROM_EMAIL,
                [sub_email],
                html_message=rendered_message,
                fail_silently=True,
            )

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Subscription(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'author')