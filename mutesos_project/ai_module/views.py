# ai_module/views.py
import json
import os
import tempfile
import re
import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.conf import settings
import speech_recognition as sr
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Try to import utilities from sos
try:
    from sos.utils import send_sos_alert, save_uploaded_audio, format_phone_number
except Exception as imp_err:
    logger.exception(f"sos.utils import failed: {imp_err}")
    send_sos_alert = None
    save_uploaded_audio = None
    def format_phone_number(x): return x

# If pydub can't find ffmpeg, uncomment and set the path:
# AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"


def _collect_active_numbers_for_user(user):
    """Return a list of formatted phone-number strings to alert for this user."""
    numbers = []
    try:
        contacts = getattr(user, 'contacts_trusted_contacts', None) or getattr(user, 'trusted_contacts', None)
        if contacts is not None:
            iterable = contacts.all() if hasattr(contacts, 'all') else contacts
            for c in (iterable.filter(is_active=True) if hasattr(iterable, 'filter') else iterable):
                num = getattr(c, 'phone_number', None) or getattr(c, 'phone', None)
                if num and isinstance(num, str) and num.strip():
                    numbers.append(format_phone_number(num.strip()))
    except Exception as e:
        logger.warning(f"Could not gather trusted contacts: {e}")

    # Helplines from contacts app (model) if available
    try:
        from contacts.models import Helpline
        helplines = Helpline.objects.filter(is_active=True)
        for h in helplines:
            num = getattr(h, 'phone_number', None) or getattr(h, 'number', None)
            if num and isinstance(num, str) and num.strip():
                numbers.append(format_phone_number(num.strip()))
    except Exception:
        # fallback to settings.EMERGENCY_HELPLINES if model unavailable
        try:
            helps = getattr(settings, 'EMERGENCY_HELPLINES', [])
            if isinstance(helps, dict):
                for num, active in helps.items():
                    if active and isinstance(num, str) and num.strip():
                        numbers.append(format_phone_number(num.strip()))
            elif isinstance(helps, (list, tuple)):
                for entry in helps:
                    if isinstance(entry, dict):
                        num = entry.get('number') or entry.get('phone') or entry.get('tel')
                        if entry.get('active', True) and isinstance(num, str) and num.strip():
                            numbers.append(format_phone_number(num.strip()))
                    elif isinstance(entry, str) and entry.strip():
                        numbers.append(format_phone_number(entry.strip()))
        except Exception as e:
            logger.warning(f"Could not gather helplines from settings: {e}")

    # dedupe while preserving order
    seen = set()
    out = []
    for n in numbers:
        if n not in seen:
            out.append(n)
            seen.add(n)
    return out


@login_required
def voice_trigger(request):
    """
    Accepts either:
      - JSON: { "transcript": "...", "latitude": "...", "longitude": "..." }
      - multipart/form-data with 'audio' file: legacy flow (will run speech recognition)
    After obtaining transcript and coords, detect keyword and send alerts to active numbers.
    """
    # ensure send_sos_alert is available
    if send_sos_alert is None:
        logger.error("send_sos_alert not available (sos.utils import failed)")
        return JsonResponse({'status': 'Server misconfigured', 'message': 'sos.utils import failed'}, status=500)

    # initialize
    transcript = ""
    latitude = request.POST.get('latitude') or request.GET.get('latitude') or ''
    longitude = request.POST.get('longitude') or request.GET.get('longitude') or ''

    # 1) If Content-Type is JSON, parse transcript+coords from body
    content_type = request.content_type or ''
    if content_type.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode('utf-8') or "{}")
            transcript = (payload.get('transcript') or "").strip()
            latitude = str(payload.get('latitude') or latitude or "")
            longitude = str(payload.get('longitude') or longitude or "")
        except Exception as e:
            logger.warning(f"Failed to parse JSON body in voice_trigger: {e}")
            return HttpResponseBadRequest("Invalid JSON")
    else:
        # 2) Fall back to file upload flow (legacy): expect 'audio' in FILES
        if request.method != "POST" or 'audio' not in request.FILES:
            return JsonResponse({'status': 'No audio or transcript received', 'spoken_text': ''})
        audio_file = request.FILES['audio']

        # Save uploaded audio (non-fatal)
        saved_path = None
        try:
            if save_uploaded_audio:
                saved_path = save_uploaded_audio(audio_file)
            else:
                logger.debug("save_uploaded_audio not available")
        except Exception as e:
            logger.warning(f"save_uploaded_audio failed: {e}")

        # create temp file and run speech recognition
        tmp_path = wav_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(getattr(audio_file, 'name', '') or '.wav')[1]) as tmp:
                for chunk in audio_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            wav_path = tmp_path + "_conv.wav"
            try:
                sound = AudioSegment.from_file(tmp_path)
            except Exception:
                # try common extensions fallback
                ext = os.path.splitext(getattr(audio_file, 'name', '') or '')[1].lower()
                ext_map = {'.m4a': 'mp4', '.mp3': 'mp3', '.ogg': 'ogg', '.webm': 'webm'}
                fmt = ext_map.get(ext, None)
                if fmt:
                    sound = AudioSegment.from_file(tmp_path, format=fmt)
                else:
                    sound = AudioSegment.from_file(tmp_path)

            sound = sound.set_frame_rate(16000).set_channels(1)
            sound.export(wav_path, format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                try:
                    transcript = recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    transcript = ""
                except sr.RequestError as e:
                    logger.warning(f"Google API error in voice_trigger: {e}")
                    try:
                        transcript = recognizer.recognize_sphinx(audio_data)
                    except Exception as sphinx_err:
                        logger.warning(f"Sphinx fallback failed: {sphinx_err}")
                        transcript = ""
        except Exception as e:
            logger.exception("Audio processing failed in voice_trigger")
            return JsonResponse({'status': 'error', 'message': f'Audio processing failed: {str(e)}'}, status=500)
        finally:
            for p in (tmp_path, wav_path):
                try:
                    if p and os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass

    # Save AIInteraction only if model exists and user provided audio or transcript
    try:
        from ai_module.models import AIInteraction
        if transcript or (request.FILES.get('audio') if hasattr(request, 'FILES') else False):
            ai = AIInteraction.objects.create(user=request.user, input_text=transcript or "", detected_danger=False)
            if 'saved_path' in locals() and saved_path:
                ai.input_voice_file = saved_path
            ai.save()
        else:
            ai = None
    except Exception as e:
        logger.debug(f"AIInteraction model not available or save failed: {e}")
        ai = None

    # Normalize and check keyword
    profile = getattr(request.user, 'profile', None)
    keyword = getattr(profile, 'voice_keyword', '') if profile else ''
    keyword_norm = re.sub(r'[^a-z0-9]', '', (keyword or "").lower())
    spoken_norm = re.sub(r'[^a-z0-9]', '', (transcript or "").lower())

    if keyword_norm and keyword_norm in spoken_norm:
        if ai:
            ai.detected_danger = True
            ai.save()

        # collect active recipients (formatted)
        recipients = _collect_active_numbers_for_user(request.user)
        results = []
        if not recipients:
            # fallback: send to user object
            try:
                r = send_sos_alert(request.user, message="🚨 Emergency Alert! Danger detected!", latitude=latitude or None, longitude=longitude or None)
                return JsonResponse({'status': '✅ SOS Triggered (fallback to user)', 'spoken_text': transcript, 'results': r})
            except Exception as e:
                logger.exception("Fallback send_sos_alert failed")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        # send alerts (SMS + call + location) to each recipient
        for number in recipients:
            try:
                res = send_sos_alert(number, message=f"🚨 Emergency Alert! {request.user.username} detected danger!", latitude=latitude or None, longitude=longitude or None)
                results.append({number: res})
            except Exception as e:
                logger.exception(f"send_sos_alert failed for {number}: {e}")
                results.append({number: {'error': str(e)}})

        return JsonResponse({'status': '✅ SOS Triggered via voice keyword!', 'spoken_text': transcript, 'results': results})

    # no keyword matched
    return JsonResponse({'status': 'No keyword detected', 'spoken_text': transcript})

