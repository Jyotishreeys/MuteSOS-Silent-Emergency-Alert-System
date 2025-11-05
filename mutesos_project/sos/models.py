from django.db import models
from django.contrib.auth.models import User


class SosAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=50)  # e.g., "passphrase", "tap"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} triggered via {self.method} at {self.timestamp}"


class Helpline(models.Model):
    name = models.CharField(max_length=100)   # e.g., Police, Ambulance
    phone_number = models.CharField(max_length=15)  # allows short numbers like 100 or 1091
    is_active = models.BooleanField(default=True)   # toggle ON/OFF

    def __str__(self):
        return f"{self.name} ({self.phone_number})"
