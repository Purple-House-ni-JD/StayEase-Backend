import uuid
from datetime import date


def generate_booking_ref() -> str:
    """
    Generate a unique booking reference in the format SE-YYYY-XXXXXXXX.
    e.g. SE-2026-3F9A12B7
    """
    year = date.today().year
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"SE-{year}-{unique_part}"


def calculate_nights(check_in: date, check_out: date) -> int:
    """Return the number of nights between two dates."""
    delta = check_out - check_in
    if delta.days <= 0:
        raise ValueError("check_out must be after check_in")
    return delta.days