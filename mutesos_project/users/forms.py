from django import forms
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, GENDER_CHOICES

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100, required=True)
    age = forms.IntegerField(required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    secret_passphrase = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Secret Passphrase for SOS'})
    )
    voice_keyword = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Voice Keyword for SOS'})
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'full_name', 'age', 'gender', 'phone', 'address',
            'secret_passphrase', 'voice_keyword'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            # Ensure profile exists
            profile, created = Profile.objects.get_or_create(user=user)
            profile.full_name = self.cleaned_data['full_name']
            profile.age = self.cleaned_data['age']
            profile.gender = self.cleaned_data['gender']
            profile.phone = self.cleaned_data['phone']
            profile.address = self.cleaned_data['address']
            profile.secret_passphrase = self.cleaned_data['secret_passphrase']  # Save secret passphrase
            profile.voice_keyword = self.cleaned_data['voice_keyword']  # ✅ Save voice keyword
            profile.save()

        return user
