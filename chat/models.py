from django.conf import settings
from django.db import models


# Create your models here.
class UserChannelSesion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    channel = models.CharField(max_length=255)
    connected_at = models.DateTimeField(auto_now_add=True)
    group = models.CharField(max_length=255, blank=True, null=True)
