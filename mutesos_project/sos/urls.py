from django.urls import path
from . import views

app_name = 'sos'

urlpatterns = [
    path('emergency/', views.emergency_trigger, name='emergency_trigger'),
    path('voice_trigger/', views.voice_trigger, name='voice_trigger'),
]
