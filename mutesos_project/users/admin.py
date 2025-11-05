from django.contrib import admin
from .models import Profile  # ✅ Import your actual model

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'age', 'gender', 'phone', 'secret_passphrase')
    search_fields = ('user__username', 'full_name', 'phone')

admin.site.register(Profile, ProfileAdmin)  # ✅ Register properly
