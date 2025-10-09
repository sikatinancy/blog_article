from django.db import models
from django.contrib.auth.models import User

class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    reply = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject} - {self.user.username if self.user else 'Anonyme'}"