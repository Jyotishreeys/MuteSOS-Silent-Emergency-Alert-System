from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Validator for Trusted Contacts (strict E.164 format)
trusted_phone_validator = RegexValidator(
    regex=r'^\+?[1-9]\d{9,14}$',
    message="Trusted contact number must be in international format (e.g., +919876543210)."
)

# Validator for Helplines (allow short like 100, 108, or international like +919876543210)
helpline_phone_validator = RegexValidator(
    regex=r'^(\+?[1-9]\d{9,14}|\d{3,5})$',
    message="Helpline number must be either a short code (e.g., 100) or international format (e.g., +919876543210)."
)

class TrustedContact(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contacts_trusted_contacts'
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, validators=[trusted_phone_validator])
    email = models.EmailField()
    relationship = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"


class Helpline(models.Model):
    label = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, validators=[helpline_phone_validator])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.label} - {self.phone_number}"
