"""Listing, browsing and deleting registered days."""

from __future__ import annotations

from collections.abc import Sequence

from ..database.models import Record
from ..ui import interface as ui
from ..utils.calculations import format_duration, format_time, get_balance_color
from ..utils.pagination import clamp_page, page_count
from ..utils.validation import parse_date
from .context import Context

PAGE_SIZE = 10


def _columns(ctx: Context) -> list[ui.Column]:
    return [
        (ctx.t("table_date"), {"style": "dim", "justify": "center"}),
        (ctx.t("work_label"), {"justify": "right"}),
        (ctx.t("balance_short_label"), {"justify": "right"}),
    ]


def format_rows(records: Sequence[Record]) -> list[list[str]]:
    """Turns records into the rows of the history table."""
    rows = []
    for record in records:
        color = get_balance_color(record["difference"])
        rows.append(
            [
                record["date"],
                format_duration(record["hours"], record["minutes"]),
                f"[{color}]{format_time(record['difference'])}[/{color}]",
            ]
        )
    return rows


def list_records(ctx: Context, limit: int) -> None:
    """Prints the last ``limit`` records of the active project (all of them if ``limit <= 0``)."""
    project_id = ctx.db.get_active_project_id()
    records = ctx.db.get_records(project_id, limit=limit if limit > 0 else None)
    if not records:
        ui.print_message(f"\n{ctx.t('no_records')}", style="yellow")
        return
    title = (
        ctx.t("full_history_header") if limit <= 0 else ctx.t("recent_records_header", limit=limit)
    )
    ui.render_header(title)
    ui.render_table("", _columns(ctx), format_rows(records))


def browse_history(ctx: Context) -> None:
    """Interactive history: pages of ``PAGE_SIZE`` rows, with next, previous, delete and back."""
    project_id = ctx.db.get_active_project_id()
    page = 0
    while True:
        total = ctx.db.count_records(project_id)
        if total == 0:
            ui.print_message(f"\n{ctx.t('no_records')}", style="yellow")
            ctx.pause()
            return

        page = clamp_page(page, total, PAGE_SIZE)
        pages = page_count(total, PAGE_SIZE)
        records = ctx.db.get_records(project_id, limit=PAGE_SIZE, offset=page * PAGE_SIZE)

        ui.clear_screen()
        ui.render_header(ctx.t("full_history_header"))
        ui.render_table("", _columns(ctx), format_rows(records))
        ui.print_message(
            f"\n {ctx.t('pagination_info', current=page + 1, total=pages, count=total)}"
        )

        options = [("V", ctx.t("pagination_back"))]
        if page < pages - 1:
            options.append(("N", ctx.t("pagination_next")))
        if page > 0:
            options.append(("P", ctx.t("pagination_prev")))
        options.append(("D", ctx.t("delete_record_option")))
        ui.render_navigation_help(options)

        choice = ui.ask_string(
            ctx.t("choose_option"), default="v", choices=[key.lower() for key, _ in options]
        ).lower()
        if choice == "n":
            page += 1
        elif choice == "p":
            page -= 1
        elif choice == "d":
            delete_record_flow(ctx, project_id)
        else:
            return


def delete_record_flow(ctx: Context, project_id: int) -> None:
    """Shows the latest days, asks for one, confirms and deletes it."""
    records = ctx.db.get_records(project_id, limit=PAGE_SIZE)
    ui.clear_screen()
    if not records:
        ui.print_message(f"\n{ctx.t('no_records')}", style="yellow")
        ctx.pause()
        return

    ui.render_header(ctx.t("delete_record_option"))
    ui.render_table("", _columns(ctx), format_rows(records))
    ui.print_message("")

    typed_date = ui.ask_string(ctx.t("delete_date_prompt"), default="").strip()
    if not typed_date:
        ui.print_message(ctx.t("op_cancelled"), style="yellow")
        ctx.pause()
        return

    target_date = parse_date(typed_date)
    record = ctx.db.get_record_by_date(project_id, target_date) if target_date else None
    if record is None:
        ui.print_message(ctx.t("delete_record_not_found", date=ui.escape(typed_date)), style="red")
        ctx.pause()
        return

    message = ctx.t(
        "delete_record_confirm",
        date=record["date"],
        hours=record["hours"],
        minutes=record["minutes"],
        diff=format_time(record["difference"]),
    )
    if ctx.confirm(message):
        ctx.db.delete_record(project_id, record["date"])
        ui.print_message(ctx.t("delete_success", date=record["date"]), style="green")
    else:
        ui.print_message(ctx.t("op_cancelled"), style="yellow")
    ctx.pause()
