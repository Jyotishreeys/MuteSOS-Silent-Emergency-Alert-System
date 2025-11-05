# sos/helpers.py
def format_phone_number(number):
    """
    Format the phone number to include country code if missing.
    Example: '9876543210' → '+919876543210' (for India)
    """
    number = str(number).strip()
    if not number.startswith('+'):
        # Default to India code (+91) – change if needed
        number = '+91' + number
    return number
