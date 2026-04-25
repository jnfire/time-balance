from datetime import date, datetime
from ..utils.calculations import format_time, calculate_balance_difference
from ..ui import interface as ui
from ..utils.i18n import translate
from ..database.manager import db

def request_date(lang: str = "en") -> str:
    """Requests date from user using UI interface."""
    today_date_str = date.today().strftime("%Y-%m-%d")
    ui.print_message(f"\n{translate('date_prompt', lang=lang, today=today_date_str)}", style="bold yellow")
    
    user_date_input = ui.ask_string(
        translate("date_input", lang=lang),
        default=today_date_str
    ).strip()

    try:
        datetime.strptime(user_date_input, "%Y-%m-%d")
        return user_date_input
    except ValueError:
        ui.print_message(translate('invalid_date', lang=lang), style="bold red")
        return today_date_str


def register_day(lang: str = "en"):
    """Interactive flow to register working hours for the active project."""
    active_project_id = db.get_active_project_id()
    current_project = db.get_project_by_id(active_project_id)
    target_work_date = request_date(lang=lang)

    existing_time_record = db.get_record_by_date(active_project_id, target_work_date)
    if existing_time_record:
        ui.print_message(f"\n{translate('duplicate_warning', lang=lang, date=target_work_date)}", style="bold yellow")
        ui.print_message(f"   {translate('previous_record', lang=lang, hours=existing_time_record['hours'], minutes=existing_time_record['minutes'])}")
        
        user_confirmed_overwrite = ui.ask_confirm(translate("overwrite_confirm", lang=lang), default=False)
        if not user_confirmed_overwrite:
            ui.print_message(translate('op_cancelled', lang=lang), style="blue")
            return

    ui.print_message(f"\n{translate('input_header', lang=lang, date=target_work_date)}", style="bold cyan")
    try:
        worked_hours_input = int(ui.ask_string(translate("hours_worked", lang=lang), default="0"))
        worked_minutes_input = int(ui.ask_string(translate("minutes_worked", lang=lang), default="0"))
    except ValueError:
        ui.print_message(translate('error_integers', lang=lang), style="bold red")
        return

    balance_difference_minutes = calculate_balance_difference(
        worked_hours=worked_hours_input,
        worked_minutes=worked_minutes_input,
        base_hours=current_project["base_hours"],
        base_minutes=current_project["base_minutes"]
    )

    db.upsert_record(
        active_project_id, 
        target_work_date, 
        worked_hours_input, 
        worked_minutes_input, 
        balance_difference_minutes
    )

    ui.print_message(f"\n{translate('save_success', lang=lang, date=target_work_date)}", style="bold green")
    ui.print_message(f"   {translate('day_diff', lang=lang, diff=format_time(balance_difference_minutes))}")
