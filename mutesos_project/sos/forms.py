from django import forms
from .models import Helpline


class SecretPassphraseForm(forms.Form):
    passphrase = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Secret Passphrase'}),
        label='Secret Passphrase'
    )


class HelplineForm(forms.ModelForm):
    class Meta:
        model = Helpline
        fields = ['name', 'phone_number', 'is_active']

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        # Allow numbers like "100", "1091", "+919876543210"
        if not phone.isdigit() and not (phone.startswith("+") and phone[1:].isdigit()):
            raise forms.ValidationError("Enter a valid phone number (e.g., 100 or +919876543210).")
        return phone
