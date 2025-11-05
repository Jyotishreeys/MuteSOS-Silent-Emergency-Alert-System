from django.shortcuts import render
from contacts.models import Helpline  # optional: to show active helplines on home

# -----------------------------
# Home Page
# -----------------------------
def home(request):
    """
    Render the main home page with optional active helplines.
    """
    helplines = Helpline.objects.filter(is_active=True) if 'contacts' in [app.name for app in Helpline._meta.apps.get_app_configs()] else []
    context = {
        'helplines': helplines
    }
    return render(request, 'emergency/home.html', context)


# -----------------------------
# Emergency Trigger (placeholder)
# -----------------------------
def emergency_trigger(request):
    """
    Placeholder for SOS trigger functionality.
    """
    # TODO: Implement actual SOS logic here
    return render(request, 'emergency/home.html', {'message': 'Emergency Triggered!'})
