# ai_module/models.py
from django.db import models
from django.contrib.auth.models import User

class AIInteraction(models.Model):
    """
    Stores each user interaction with the AI (voice/text input).
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ai_interactions'
    )
    input_text = models.TextField(blank=True, null=True)
    input_voice_file = models.FileField(
        upload_to='voice_inputs/', blank=True, null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    detected_danger = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class VoiceAnalysis(models.Model):
    """
    Stores the AI analysis of the user's voice input, including
    danger level and confidence score.
    """
    DANGER_LEVEL_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    interaction = models.OneToOneField(
        AIInteraction, on_delete=models.CASCADE, related_name='voice_analysis'
    )
    confidence_score = models.FloatField(default=0)
    danger_level = models.CharField(
        max_length=10, choices=DANGER_LEVEL_CHOICES, default='Low'
    )

    def __str__(self):
        return f"{self.interaction.user.username} - {self.danger_level}"

