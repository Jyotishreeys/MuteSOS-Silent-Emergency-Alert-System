# sos/views.py
import os
import tempfile
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dotenv import load_dotenv
from django.http import JsonResponse
import speech_recognition as sr
from pydub import AudioSegment

from .forms import SecretPassphraseForm
from ai_module.models import AIInteraction
from users.models import Profile
from contacts.models import TrustedContact, Helpline
from .utils import send_sos_alert, save_uploaded_audio

# Load environment variables
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

logger = logging.getLogger(__name__)

# -------------------------
# Phone formatting helper
# -------------------------
def format_phone_number(number):
    """Format phone number to include +91 if missing (India default)."""
    number = number.strip()
    if number.startswith('+'):
        return number
    if number.startswith('0') and len(number) == 11:
        return '+91' + number[1:]
    if len(number) == 10 and number.isdigit():
        return '+91' + number
    return number

# -------------------------
# Emergency Trigger View
# -------------------------
@login_required
def emergency_trigger(request):
    triggered = False
    passphrase_form = SecretPassphraseForm()
    results_summary = []

    active_contacts = request.user.contacts_trusted_contacts.filter(is_active=True)
    active_helplines = Helpline.objects.filter(is_active=True)
    profile = getattr(request.user, 'profile', None)
    voice_keyword = profile.voice_keyword.lower() if profile and profile.voice_keyword else None

    if request.method == 'POST':
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        maps_link = f"\n📍 Location: https://www.google.com/maps?q={latitude},{longitude}" if latitude and longitude else ""

        recipients = [c.phone_number for c in active_contacts] + [h.phone_number for h in active_helplines]

        # -------------------------
        # Manual SOS Trigger
        # -------------------------
        if 'trigger_button' in request.POST:
            if recipients:
                for number in recipients:
                    formatted_number = format_phone_number(number)
                    res = send_sos_alert(
                        formatted_number,
                        message=f"🚨 MuteSOS Alert: {request.user.username} triggered SOS!{maps_link}",
                    )
                    results_summary.append({formatted_number: res})
                triggered = True
                messages.success(request, "✅ SOS sent to all active contacts and helplines!")
            else:
                messages.warning(request, "⚠️ No active contacts or helplines found.")

        # -------------------------
        # Secret Passphrase Trigger
        # -------------------------
        elif 'passphrase' in request.POST:
            passphrase_form = SecretPassphraseForm(request.POST)
            if passphrase_form.is_valid():
                entered_pass = passphrase_form.cleaned_data['passphrase']
                if profile and profile.secret_passphrase and entered_pass == profile.secret_passphrase:
                    if recipients:
                        for number in recipients:
                            formatted_number = format_phone_number(number)
                            res = send_sos_alert(
                                formatted_number,
                                message=f"🚨 MuteSOS Alert: {request.user.username} triggered SOS via secret passphrase!{maps_link}",
                            )
                            results_summary.append({formatted_number: res})
                        triggered = True
                        messages.success(request, "✅ SOS triggered via secret passphrase!")
                    else:
                        messages.warning(request, "⚠️ No active contacts or helplines found.")
                else:
                    messages.error(request, "❌ Invalid secret passphrase.")

    return render(request, "sos/emergency_trigger.html", {
        'triggered': triggered,
        'passphrase_form': passphrase_form,
        'active_contacts': active_contacts,
        'active_helplines': active_helplines,
        'voice_keyword': voice_keyword,
        'results_summary': results_summary,
    })


# -------------------------
# Voice Trigger View
# -------------------------
@login_required
def voice_trigger(request):
    if request.method != "POST" or 'audio' not in request.FILES:
        return JsonResponse({'status': 'No audio received', 'spoken_text': ''})

    audio_file = request.FILES['audio']

    # Save audio
    saved_path = save_uploaded_audio(audio_file)
    interaction = AIInteraction.objects.create(user=request.user, input_voice_file=saved_path, detected_danger=False)

    tmp_path, wav_path, spoken_text = None, None, ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        wav_path = tmp_path + ".wav"
        sound = AudioSegment.from_file(tmp_path)
        sound.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            try:
                spoken_text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                spoken_text = ""
            except sr.RequestError:
                spoken_text = "[Google API error]"

    except Exception as e:
        logger.exception("Audio processing failed")
        return JsonResponse({'status': 'error', 'message': f'Audio processing failed: {str(e)}'})

    finally:
        for path in [tmp_path, wav_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

    # Save spoken text
    interaction.input_text = spoken_text
    interaction.save()

    # Check voice keyword
    profile = getattr(request.user, 'profile', None)
    keyword = getattr(profile, 'voice_keyword', '').lower().strip() if profile else ""
    results_summary = []

    if keyword and spoken_text and keyword in spoken_text.lower():
        interaction.detected_danger = True
        interaction.save()

        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        maps_link = f"\n📍 Location: https://www.google.com/maps?q={latitude},{longitude}" if latitude and longitude else ""

        recipients = [c.phone_number for c in request.user.contacts_trusted_contacts.filter(is_active=True)] + \
                     [h.phone_number for h in Helpline.objects.filter(is_active=True)]
        for number in recipients:
            formatted_number = format_phone_number(number)
            res = send_sos_alert(
                formatted_number,
                message=f"🚨 MuteSOS Alert: {request.user.username} triggered SOS via voice keyword!{maps_link}",
            )
            results_summary.append({formatted_number: res})

        return JsonResponse({
            'status': '✅ SOS Triggered via voice keyword!',
            'spoken_text': spoken_text,
            'results': results_summary
        })

    return JsonResponse({'status': 'No keyword detected', 'spoken_text': spoken_text})


# -------------------------
# Companion AI Placeholder
# -------------------------
@login_required
def companion(request):
    if request.method == "POST":
        return JsonResponse({'status': 'Companion active'})
    return JsonResponse({'status': 'Companion ready'})
