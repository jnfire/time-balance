def format_time(total_minutes: int) -> str:
    """Converts minutes to a signed, readable format: +1h 5m, -25m, +2h, 0m."""
    if total_minutes == 0:
        return "0m"

    time_sign = "+" if total_minutes > 0 else "-"
    hours_part, minutes_part = divmod(abs(total_minutes), 60)

    parts = []
    if hours_part:
        parts.append(f"{hours_part}h")
    if minutes_part:
        parts.append(f"{minutes_part}m")
    return f"{time_sign}{' '.join(parts)}"


def format_duration(hours: int, minutes: int) -> str:
    """Formats an unsigned duration: 8h, 7h 45m, 25m, 0m."""
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts) or "0m"


def get_balance_color(total_minutes: int) -> str:
    """Returns the color associated with a balance value."""
    if total_minutes > 0:
        return "green"
    if total_minutes < 0:
        return "red"
    return "dim"


def calculate_balance_difference(
    worked_hours: int, worked_minutes: int, base_hours: int, base_minutes: int
) -> int:
    """Calculates the difference in minutes between worked time and base time."""
    total_base_minutes = (base_hours * 60) + base_minutes
    total_worked_minutes = (worked_hours * 60) + worked_minutes
    return total_worked_minutes - total_base_minutes


def calculate_total_balance_from_records(records_dict: dict[str, dict]) -> int:
    """Iterates through all records and sums differences."""
    accumulated_balance = 0
    for _record_date, record_info in records_dict.items():
        accumulated_balance += record_info.get("difference", 0)
    return accumulated_balance
