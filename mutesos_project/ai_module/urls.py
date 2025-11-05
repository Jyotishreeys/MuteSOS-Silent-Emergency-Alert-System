from django.urls import path
from . import views

app_name = 'ai_module'

urlpatterns = [
    path('voice_trigger/', views.voice_trigger, name='voice_trigger'),
]
