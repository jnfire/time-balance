"""Command-line entry point: the interactive control center and the quick flags."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .. import config
from ..database import get_database
from ..ui import interface as ui
from ..utils.calculations import format_duration, format_time, get_balance_color
from .config_menu import config_menu
from .context import Context
from .history import browse_history, list_records
from .projects import project_menu
from .registration import register_day

MENU_OPTIONS = ("1", "2", "3", "4", "5")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="time-balance",
        description="Register your workdays and keep your hour balance.",
    )
    parser.add_argument(
        "-s", "--status", action="store_true", help="Show only the accumulated balance."
    )
    parser.add_argument(
        "-l",
        "--list",
        type=int,
        nargs="?",
        const=5,
        metavar="N",
        help="List the last N records (default 5, 0 lists all of them).",
    )
    parser.add_argument("--version", action="store_true", help="Show the application version.")
    parser.add_argument(
        "--lang",
        choices=["en", "es", "auto"],
        default="auto",
        help="Force the interface language.",
    )
    return parser


def _colored(minutes: int) -> str:
    color = get_balance_color(minutes)
    return f"[{color}]{format_time(minutes)}[/{color}]"


def display_dashboard(ctx: Context) -> None:
    """The panel with the active project, its daily base, its balance and its last record."""
    project = ctx.db.get_active_project()
    rows = [
        (ctx.t("project_label"), ui.escape(project["name"])),
        (
            ctx.t("base_day_label"),
            format_duration(project["base_hours"], project["base_minutes"]),
        ),
        (ctx.t("balance_label"), _colored(ctx.db.get_total_balance(project["id"]))),
    ]
    latest = ctx.db.get_records(project["id"], limit=1)
    if latest:
        record = latest[0]
        rows.append(
            (
                ctx.t("last_record_label"),
                f"{record['date']} · {format_duration(record['hours'], record['minutes'])}"
                f" · {_colored(record['difference'])}",
            )
        )
    ui.render_summary_panel(ctx.t("dashboard_title"), rows, subtitle=f"v{config.VERSION}")


def interactive_menu(ctx: Context) -> None:
    """The control center. Runs until the user chooses to leave."""
    while True:
        ui.clear_screen()
        display_dashboard(ctx)
        ui.print_message("")
        for number in MENU_OPTIONS:
            ui.print_message(f" [bold blue]{number}.[/bold blue] {ctx.t(f'option_{number}_clean')}")

        choice = ui.ask_string(f"\n{ctx.t('choose_option')}", choices=MENU_OPTIONS)
        if choice == "1":
            register_day(ctx)
            ctx.pause()
        elif choice == "2":
            browse_history(ctx)
        elif choice == "3":
            ctx = config_menu(ctx)
        elif choice == "4":
            project_menu(ctx)
        else:
            ui.print_message(f"\n{ctx.t('exit_msg')}", style="bold blue")
            return


def main(argv: Sequence[str] | None = None) -> int:
    """Runs the program and returns the exit code."""
    args = build_parser().parse_args(argv)

    if args.version:
        ui.print_message(f"time-balance [bold blue]v{config.VERSION}[/bold blue]")
        return 0

    ctx = Context.from_settings(get_database())
    if args.lang != "auto":
        ctx = ctx.with_lang(args.lang)

    if args.status:
        project = ctx.db.get_active_project()
        ui.print_message(
            ctx.t("status_project", name=ui.escape(project["name"])), style="bold blue"
        )
        ui.print_message(
            ctx.t("status_balance", balance=_colored(ctx.db.get_total_balance(project["id"]))),
            style="bold",
        )
        return 0

    if args.list is not None:
        list_records(ctx, args.list)
        return 0

    try:
        interactive_menu(ctx)
    except KeyboardInterrupt:
        ui.print_message(f"\n\n {ctx.t('op_cancelled')} ", style="yellow")
    return 0
