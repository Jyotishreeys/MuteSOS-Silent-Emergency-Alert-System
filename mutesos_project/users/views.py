# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm
from .models import Profile
from django import forms

# -----------------------------
# Profile Update Form
# -----------------------------
class ProfileUpdateForm(forms.ModelForm):
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
        model = Profile
        fields = [
            'full_name', 'age', 'gender', 'phone', 'address',
            'secret_passphrase', 'voice_keyword'
        ]


# -----------------------------
# Home Page
# -----------------------------
def home(request):
    return render(request, 'emergency/home.html')


# -----------------------------
# User Registration
# -----------------------------
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Ensure profile exists and save extra fields
            profile, created = Profile.objects.get_or_create(user=user)
            profile.full_name = form.cleaned_data['full_name']
            profile.age = form.cleaned_data['age']
            profile.gender = form.cleaned_data['gender']
            profile.phone = form.cleaned_data['phone']
            profile.address = form.cleaned_data['address']
            profile.secret_passphrase = form.cleaned_data.get('secret_passphrase', '')
            profile.voice_keyword = form.cleaned_data.get('voice_keyword', '')
            profile.save()

            messages.success(request, "✅ Account created successfully! You can now log in.")
            return redirect('users:login')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


# -----------------------------
# User Profile (View + Update)
# -----------------------------
@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect('users:profile')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=profile)

    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'users/profile.html', context)
