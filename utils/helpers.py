import re
import secrets
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return current UTC time as a naive datetime (no deprecation warning)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_referral_code(telegram_id: int) -> str:
    """Generate a unique 8-char referral code using cryptographic randomness."""
    return secrets.token_hex(4).upper()


def is_valid_instagram_username(username: str) -> bool:
    """Validate Instagram username format."""
    pattern = r"^[a-zA-Z0-9_.]{1,30}$"
    return bool(re.match(pattern, username))


def clean_instagram_username(text: str) -> str:
    """Strip @ and whitespace from user input."""
    return text.strip().lstrip("@").strip()


def format_datetime_fr(iso_str: str) -> str:
    """Format an ISO datetime string to French date."""
    try:
        dt = datetime.fromisoformat(iso_str)
        months = [
            "", "janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre",
        ]
        return f"{dt.day} {months[dt.month]} {dt.year}"
    except (ValueError, TypeError):
        return iso_str or "—"


def format_relative_time_fr(iso_str: str) -> str:
    """Format ISO datetime as relative time in French."""
    try:
        dt = datetime.fromisoformat(iso_str)
        now = utcnow()
        delta = dt - now
        if delta.total_seconds() <= 0:
            return "expiré"
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        if hours > 0:
            return f"{hours}h{minutes:02d}"
        return f"{minutes} min"
    except (ValueError, TypeError):
        return "—"
