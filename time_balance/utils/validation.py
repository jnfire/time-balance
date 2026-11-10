"""Parsing and validation of what the user types. No terminal and no database in here."""

from __future__ import annotations

from datetime import datetime

MAX_HOURS_PER_DAY = 24


class InputError(ValueError):
    """The user typed something invalid. ``message_key`` is the translation to show."""

    def __init__(self, message_key: str) -> None:
        super().__init__(message_key)
        self.message_key = message_key


def parse_date(text: str) -> str | None:
    """Returns the date as ``YYYY-MM-DD`` if ``text`` is a valid one, otherwise None."""
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return None


def parse_duration(hours_text: str, minutes_text: str) -> tuple[int, int]:
    """Parses a duration typed as hours and minutes.

    Raises ``InputError`` when a part is not an integer (``error_integers``) or the
    duration is negative, has 60 or more minutes, or exceeds a full day (``error_range``).
    """
    try:
        hours = int(hours_text)
        minutes = int(minutes_text)
    except ValueError:
        raise InputError("error_integers") from None
    if hours < 0 or not 0 <= minutes <= 59 or hours * 60 + minutes > MAX_HOURS_PER_DAY * 60:
        raise InputError("error_range")
    return hours, minutes
