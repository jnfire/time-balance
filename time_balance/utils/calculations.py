from typing import Dict

def format_time(total_minutes: int) -> str:
    """Converts minutes to readable format +/- Xh Ym."""
    if total_minutes == 0:
        return "0h 0m"
        
    time_sign = "+" if total_minutes > 0 else "-"
    absolute_minutes = abs(total_minutes)
    hours_part = absolute_minutes // 60
    minutes_part = absolute_minutes % 60
    
    return f"{time_sign}{hours_part}h {minutes_part}m"


def get_balance_color(total_minutes: int) -> str:
    """Returns the color associated with a balance value."""
    if total_minutes > 0:
        return "green"
    elif total_minutes < 0:
        return "red"
    return "dim"


def calculate_balance_difference(worked_hours: int, worked_minutes: int, base_hours: int, base_minutes: int) -> int:
    """Calculates the difference in minutes between worked time and base time."""
    total_base_minutes = (base_hours * 60) + base_minutes
    total_worked_minutes = (worked_hours * 60) + worked_minutes
    return total_worked_minutes - total_base_minutes


def calculate_total_balance_from_records(records_dict: Dict[str, dict]) -> int:
    """Iterates through all records and sums differences."""
    accumulated_balance = 0
    for _record_date, record_info in records_dict.items():
        accumulated_balance += record_info.get('difference', 0)
    return accumulated_balance
