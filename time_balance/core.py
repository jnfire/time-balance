def format_time(total_minutes):
    """Converts minutes to readable format +/- Xh Ym."""
    sign = ""
    if total_minutes < 0:
        sign = "-"
        total_minutes = abs(total_minutes)

    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{sign}{hours}h {minutes}m"


def calculate_total_balance(records):
    """Iterates through all records and sums differences."""
    balance = 0
    for _date, info in records.items():
        # Using English key 'difference'
        balance += info['difference']
    return balance
