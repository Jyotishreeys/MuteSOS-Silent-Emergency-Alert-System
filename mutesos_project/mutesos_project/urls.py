from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # <-- add this import

urlpatterns = [
    path('admin/', admin.site.urls),

    # Emergency app (homepage & core emergency features)
    path('', include('emergency.urls', namespace='emergency')),

    # Users app
    path('user/', include('users.urls', namespace='users')),

    # SOS app
    path('sos/', include('sos.urls', namespace='sos')),

    # Trusted Contacts / Helplines app
    path('contacts/', include('contacts.urls', namespace='contacts')),

    # AI Module app (Companion AI + Voice Trigger)
    path('ai_module/', include('ai_module.urls', namespace='ai_module')),

    # Offline page for PWA
    path('offline/', TemplateView.as_view(template_name="offline.html"), name='offline'),
]
