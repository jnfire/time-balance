from datetime import date, datetime
from ..utils.calculations import format_time
from ..ui import interface as ui
from ..utils.i18n import translate
from ..database.manager import db

def request_date(lang: str = "en") -> str:
    """Requests date from user using UI interface."""
    today = date.today().strftime("%Y-%m-%d")
    ui.print_message(f"\n{translate('date_prompt', lang=lang, today=today)}", style="bold yellow")
    
    date_input = ui.ask_string(
        translate("date_input", lang=lang),
        default=today
    ).strip()

    try:
        datetime.strptime(date_input, "%Y-%m-%d")
        return date_input
    except ValueError:
        ui.print_message(translate('invalid_date', lang=lang), style="bold red")
        return today


def register_day(lang: str = "en"):
    """Interactive flow to register working hours for the active project."""
    active_id = db.get_active_project_id()
    project = db.get_project_by_id(active_id)
    work_date = request_date(lang=lang)

    existing_record = db.get_record_by_date(active_id, work_date)
    if existing_record:
        ui.print_message(f"\n{translate('duplicate_warning', lang=lang, date=work_date)}", style="bold yellow")
        ui.print_message(f"   {translate('previous_record', lang=lang, hours=existing_record['hours'], minutes=existing_record['minutes'])}")
        
        if not ui.ask_confirm(translate("overwrite_confirm", lang=lang), default=False):
            ui.print_message(translate('op_cancelled', lang=lang), style="blue")
            return

    ui.print_message(f"\n{translate('input_header', lang=lang, date=work_date)}", style="bold cyan")
    try:
        hours = int(ui.ask_string(translate("hours_worked", lang=lang), default="0"))
        minutes = int(ui.ask_string(translate("minutes_worked", lang=lang), default="0"))
    except ValueError:
        ui.print_message(translate('error_integers', lang=lang), style="bold red")
        return

    base_minutes = (project["base_hours"] * 60) + project["base_minutes"]
    worked_minutes = (hours * 60) + minutes
    difference = worked_minutes - base_minutes

    db.upsert_record(active_id, work_date, hours, minutes, difference)

    ui.print_message(f"\n{translate('save_success', lang=lang, date=work_date)}", style="bold green")
    ui.print_message(f"   {translate('day_diff', lang=lang, diff=format_time(difference))}")
