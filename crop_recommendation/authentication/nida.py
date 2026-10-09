"""
NIDA (National Identification Authority) number helpers.

A NIDA number is 20 digits, usually written as YYYYMMDD-XXXXX-XXXXX-XX.
The first 8 digits are the holder's date of birth. We store only the digits.

Two levels of checking:
  1. `nida_problem` runs offline checks (length, a real birth date, minimum age).
     These run on every sign-up and profile update.
  2. `verify_nida` confirms the number with the NIDA service. It is a placeholder
     until NIDA integration is added; see the TODO below.
"""
import re
from datetime import date

NIDA_LENGTH = 20
MIN_SELLER_AGE = 18


def normalize_nida(value):
    """Strip spaces and dashes, keeping only digits."""
    return re.sub(r"\D", "", value or "")


def nida_birth_date(value):
    """Date of birth encoded in the first 8 digits, or None if it is not a real date."""
    digits = normalize_nida(value)
    if len(digits) < 8:
        return None
    try:
        return date(int(digits[:4]), int(digits[4:6]), int(digits[6:8]))
    except ValueError:
        return None


def _age_on(born, today):
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def nida_problem(value, today=None):
    """Return a message describing what is wrong with the number, or None if it looks valid."""
    if len(normalize_nida(value)) != NIDA_LENGTH:
        return "Enter a valid 20-digit NIDA number."
    born = nida_birth_date(value)
    today = today or date.today()
    if born is None or born > today or born.year < 1900:
        return ("This is not a valid NIDA number. The first 8 digits should be "
                "your date of birth (YYYYMMDD).")
    if _age_on(born, today) < MIN_SELLER_AGE:
        return f"You must be at least {MIN_SELLER_AGE} years old to register with a NIDA number."
    return None


def is_valid_nida_format(value):
    return nida_problem(value) is None


def format_nida(value):
    """Return the number in the familiar YYYYMMDD-XXXXX-XXXXX-XX layout."""
    digits = normalize_nida(value)
    if len(digits) != NIDA_LENGTH:
        return value
    return f"{digits[:8]}-{digits[8:13]}-{digits[13:18]}-{digits[18:]}"


def verify_nida(nida_number, first_name, last_name):
    """
    Confirm the number with the NIDA service.

    Return True when NIDA confirms the number belongs to this person,
    False when NIDA says it does not, and None when verification is unavailable.

    TODO (NIDA integration): call the NIDA API here using credentials from .env
    (e.g. NIDA_API_URL / NIDA_API_KEY read via django.conf.settings), compare the
    returned names with first_name / last_name, and return True or False.
    Until then this returns None and admins can verify sellers manually in the
    Django admin ("Mark NIDA as verified").
    """
    return None
