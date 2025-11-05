# sos/utils.py
import os
import time
import logging
import traceback
from django.conf import settings
from twilio.rest import Client
from dotenv import load_dotenv
from .helpers import format_phone_number

# Setup logger
logger = logging.getLogger(__name__)

# Load environment variables (safe to call again)
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# -----------------------------
# Twilio alert functions
# -----------------------------
def send_sms_alert(to_number, message):
    """
    Send SMS via Twilio.
    Returns a dict: {"to": str, "sent": bool, "sid": Optional[str], "error": Optional[str]}
    """
    result = {"to": to_number, "sent": False, "sid": None, "error": None}
    try:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
            msg = "Twilio credentials missing — skipping SMS send"
            logger.warning(msg)
            result["error"] = "missing_credentials"
            return result

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        formatted = format_phone_number(to_number)
        msg_obj = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=formatted
        )
        sid = getattr(msg_obj, "sid", None)
        status = getattr(msg_obj, "status", None)
        logger.info(f"SMS sent to {formatted} sid={sid} status={status}")
        result.update({"to": formatted, "sent": True, "sid": sid, "status": status})
        return result

    except Exception as e:
        tb = traceback.format_exc()
        logger.exception(f"❌ SMS alert error to {to_number}: {e}\n{tb}")
        result["error"] = str(e)
        result["traceback"] = tb
        return result


def make_call_alert(to_number, message):
    """
    Place voice call via Twilio.
    Returns a dict: {"to": str, "placed": bool, "sid": Optional[str], "error": Optional[str]}
    """
    result = {"to": to_number, "placed": False, "sid": None, "error": None}
    try:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
            msg = "Twilio credentials missing — skipping call"
            logger.warning(msg)
            result["error"] = "missing_credentials"
            return result

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        formatted = format_phone_number(to_number)

        # TwiML inline message
        twiml = f'<Response><Say voice="alice">{message}</Say></Response>'

        call_obj = client.calls.create(
            twiml=twiml,
            from_=TWILIO_PHONE_NUMBER,
            to=formatted
        )
        sid = getattr(call_obj, "sid", None)
        status = getattr(call_obj, "status", None)
        logger.info(f"Call placed to {formatted} sid={sid} status={status}")
        result.update({"to": formatted, "placed": True, "sid": sid, "status": status})
        return result

    except Exception as e:
        tb = traceback.format_exc()
        logger.exception(f"❌ Call alert error to {to_number}: {e}\n{tb}")
        result["error"] = str(e)
        result["traceback"] = tb
        return result

# -----------------------------
# Helper: normalize helplines config
# -----------------------------
def _iter_active_helplines():
    """
    Yield phone-number strings for helplines that should be alerted.
    Accepts multiple shapes for settings.EMERGENCY_HELPLINES:
      - list of strings: ["100", "+911234..."]
      - list of dicts: [{"number": "100", "active": False}, {"number": "+911234...", "active": True}]
      - dict mapping: {"100": False, "+911234...": True}
    """
    helplines = getattr(settings, 'EMERGENCY_HELPLINES', [])
    if not helplines:
        return

    if isinstance(helplines, dict):
        for num, active in helplines.items():
            if active and isinstance(num, str) and num.strip():
                yield num.strip()
        return

    if isinstance(helplines, (list, tuple)):
        for entry in helplines:
            if isinstance(entry, str):
                if entry.strip():
                    yield entry.strip()
            elif isinstance(entry, dict):
                num = entry.get('number') or entry.get('phone') or entry.get('tel')
                active = entry.get('active', True)
                if active and isinstance(num, str) and num.strip():
                    yield num.strip()
            else:
                logger.debug(f"Skipping unknown helpline entry type: {entry!r}")
        return

    logger.debug("EMERGENCY_HELPLINES has unsupported type; expected dict or list/tuple")


# -----------------------------
# SOS Alert wrapper
# -----------------------------
def send_sos_alert(user_or_number, message=None, latitude=None, longitude=None):
    """
    Trigger SOS alert.
    Works for:
      - user_or_number as a User instance: sends to trusted contacts and active helplines
      - user_or_number as a phone-number string: sends SMS+call directly

    Returns:
      {
        "ok": True/False,
        "targets": [
            {"to": "...", "sms": {...}, "call": {...}},
            ...
        ],
        "errors": [ ... ]
      }
    """
    results = {"ok": True, "targets": [], "errors": []}

    location_link = ""
    if latitude is not None and longitude is not None:
        location_link = f"\n📍 Location: https://www.google.com/maps?q={latitude},{longitude}"

    # Helper to attempt sms + call and collect results
    def _alert_number(number, full_message):
        sms_res = send_sms_alert(number, full_message)
        call_res = make_call_alert(number, full_message)
        target_entry = {"to": sms_res.get("to") or call_res.get("to") or number, "sms": sms_res, "call": call_res}
        results["targets"].append(target_entry)
        # If either failed, mark ok as False and record error
        if (not sms_res.get("sent")) or (not call_res.get("placed")):
            results["ok"] = False
            # aggregate errors
            if sms_res.get("error"):
                results["errors"].append({"to": number, "sms_error": sms_res.get("error")})
            if call_res.get("error"):
                results["errors"].append({"to": number, "call_error": call_res.get("error")})
        return target_entry

    # If a raw phone number string is passed, send directly
    if isinstance(user_or_number, str):
        full_message = (message or "🚨 Emergency Alert!") + location_link
        _alert_number(user_or_number, full_message)
        return results

    # Otherwise treat as a user object
    user = user_or_number
    # Build a readable message
    display = ""
    try:
        display = user.get_full_name() if callable(getattr(user, "get_full_name", None)) else getattr(user, "username", "")
    except Exception:
        display = getattr(user, "username", str(user))
    full_message = (message or f"⚠️ Emergency Alert! {display} needs help!") + location_link

    # Trusted contacts
    try:
        contacts = getattr(user, 'trusted_contacts', None) or getattr(user, 'trusted_contacts_set', None) or getattr(user, 'trustedcontact_set', None)
        if contacts is not None:
            iterable = contacts.all() if hasattr(contacts, 'all') else contacts
            for contact in iterable:
                number = None
                if isinstance(contact, str):
                    number = contact
                else:
                    # support model instance or dict
                    number = getattr(contact, 'phone_number', None) or getattr(contact, 'phone', None) or (contact.get('phone_number') if isinstance(contact, dict) else None)
                if number and isinstance(number, str) and number.strip():
                    try:
                        _alert_number(number, full_message)
                    except Exception as e:
                        tb = traceback.format_exc()
                        logger.exception(f"Failed alert to trusted contact {number}: {e}\n{tb}")
                        results["ok"] = False
                        results["errors"].append({"to": number, "error": str(e)})
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception(f"Failed to iterate trusted contacts for user {getattr(user, 'username', repr(user))}: {e}\n{tb}")
        results["ok"] = False
        results["errors"].append({"trusted_contacts_iteration_error": str(e)})

    # Active emergency helplines
    try:
        for helpline_num in _iter_active_helplines():
            try:
                _alert_number(helpline_num, full_message)
            except Exception as e:
                tb = traceback.format_exc()
                logger.exception(f"Failed alert to helpline {helpline_num}: {e}\n{tb}")
                results["ok"] = False
                results["errors"].append({"to": helpline_num, "error": str(e)})
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception(f"Error while sending to emergency helplines: {e}\n{tb}")
        results["ok"] = False
        results["errors"].append({"helplines_error": str(e)})

    return results


# -----------------------------
# Audio saving
# -----------------------------
def save_uploaded_audio(file):
    """
    Save uploaded audio to MEDIA_ROOT/sos_audio and return the path.
    """
    audio_dir = os.path.join(settings.MEDIA_ROOT, 'sos_audio')
    os.makedirs(audio_dir, exist_ok=True)
    timestamp = int(time.time() * 1000)
    _, ext = os.path.splitext(getattr(file, 'name', '') or '')
    ext = ext if ext else '.wav'
    filename = f"sos_audio_{timestamp}{ext}"
    file_path = os.path.join(audio_dir, filename)

    try:
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        logger.info(f"Saved audio file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save uploaded audio to {file_path}: {e}")
        raise

    return file_path


# -----------------------------
# Backward compatibility alias
# -----------------------------
send_twilio_alert = send_sos_alert
