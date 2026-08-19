from django.db import models
from django.conf import settings


class Contract(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='contracts/')
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='messages')
    question = models.TextField()
    answer = models.TextField()
    source = models.TextField(blank=True, null=True)
    asked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['asked_at']

    def __str__(self):
        return f"{self.question[:50]}"
        
        