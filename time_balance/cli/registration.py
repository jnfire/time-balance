"""Registering the hours worked on a day."""

from __future__ import annotations

from datetime import date

from ..ui import interface as ui
from ..utils.calculations import calculate_balance_difference, format_time
from ..utils.validation import InputError, parse_date, parse_duration
from .context import Context


def request_date(ctx: Context) -> str | None:
    """Asks for a date (today by default). Returns None, after saying so, if it is not valid."""
    today = date.today().isoformat()
    ui.print_message(f"\n{ctx.t('date_prompt', today=today)}", style="bold yellow")
    parsed = parse_date(ui.ask_string(ctx.t("date_input"), default=today))
    if parsed is None:
        ui.print_message(ctx.t("invalid_date"), style="bold red")
    return parsed


def register_day(ctx: Context) -> None:
    """Asks for a day and the time worked, and stores it for the active project."""
    project = ctx.db.get_active_project()
    target_date = request_date(ctx)
    if target_date is None:
        return

    existing = ctx.db.get_record_by_date(project["id"], target_date)
    if existing:
        ui.print_message(f"\n{ctx.t('duplicate_warning', date=target_date)}", style="bold yellow")
        ui.print_message(
            f"   {ctx.t('previous_record', hours=existing['hours'], minutes=existing['minutes'])}"
        )
        if not ctx.confirm(ctx.t("overwrite_confirm")):
            ui.print_message(ctx.t("op_cancelled"), style="blue")
            return

    ui.render_header(ctx.t("input_header", date=target_date))
    try:
        hours, minutes = parse_duration(
            ui.ask_string(ctx.t("hours_worked"), default="0"),
            ui.ask_string(ctx.t("minutes_worked"), default="0"),
        )
    except InputError as error:
        ui.print_message(ctx.t(error.message_key), style="bold red")
        return

    difference = calculate_balance_difference(
        hours, minutes, project["base_hours"], project["base_minutes"]
    )
    ctx.db.upsert_record(project["id"], target_date, hours, minutes, difference)

    ui.print_message(f"\n{ctx.t('save_success', date=target_date)}", style="bold green")
    ui.print_message(f"   {ctx.t('day_diff', diff=format_time(difference))}")
