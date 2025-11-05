from django.contrib import admin
from .models import Helpline
from .forms import HelplineForm


class HelplineAdmin(admin.ModelAdmin):
    form = HelplineForm
    list_display = ('name', 'phone_number', 'is_active')  # show in admin list


admin.site.register(Helpline, HelplineAdmin)


# Register your models here.
