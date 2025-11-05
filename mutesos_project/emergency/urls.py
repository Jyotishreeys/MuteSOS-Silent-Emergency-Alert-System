from django.urls import path
from . import views

app_name = 'emergency'

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('trigger/', views.emergency_trigger, name='emergency_trigger'),  # SOS trigger
]
