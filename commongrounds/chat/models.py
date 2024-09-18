# models.py
from django.db import models
from core.models import Userprofile

class Chat(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Userprofile, on_delete=models.CASCADE, related_name='chats')
    context = models.ManyToManyField(Userprofile)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=7)
    content = models.TextField()
    content_html = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    context = models.ManyToManyField(Userprofile)
    class Meta:
        ordering = ['timestamp']
