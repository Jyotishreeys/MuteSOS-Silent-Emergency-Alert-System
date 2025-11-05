from django import forms
from .models import TrustedContact, Helpline


class TrustedContactForm(forms.ModelForm):
    class Meta:
        model = TrustedContact
        fields = ['name', 'phone_number', 'email', 'relationship', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Relationship'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HelplineForm(forms.ModelForm):
    class Meta:
        model = Helpline
        fields = ['label', 'phone_number', 'is_active']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Helpline Label'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
