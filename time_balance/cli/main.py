import argparse
import sys
from ..utils.calculations import format_time
from ..ui import interface as ui
from ..database.manager import db
from ..utils.i18n import translate, get_system_language
from .. import config

# Import sibling modules
from .registration import register_day
from .history import view_history
from .config_menu import config_menu
from .projects import project_menu
from .migration import migrate_from_json

def get_current_lang() -> str:
    """Determines the active language based on settings or system."""
    lang = db.get_setting("language", "auto")
    if lang == "auto":
        return get_system_language()
    return lang


def display_dashboard(project: dict, balance: int, lang: str):
    """Prepares and sends dashboard data to the UI interface."""
    balance_fmt = format_time(balance)
    balance_color = "green" if balance >= 0 else "red"
    if balance > 0:
        balance_fmt = f"+{balance_fmt}"

    labels = {
        'project': translate('project_label', lang=lang),
        'base_day': translate('base_day_label', lang=lang),
        'balance': translate('balance_label', lang=lang),
        'dashboard_title': translate('dashboard_title', lang=lang)
    }
    
    ui.render_dashboard(
        project_name=project['name'],
        base_hours=project['base_hours'],
        base_minutes=project['base_minutes'],
        balance_fmt=balance_fmt,
        balance_color=balance_color,
        version=config.VERSION,
        labels=labels
    )


def interactive_menu():
    """Main interactive menu loop."""
    while True:
        lang = get_current_lang()
        active_id = db.get_active_project_id()
        project = db.get_project_by_id(active_id)
        total_balance = db.get_total_balance(active_id)

        ui.clear_screen()
        display_dashboard(project, total_balance, lang)

        ui.print_message(f"\n [bold cyan]1.[/bold cyan] {translate('option_1_clean', lang=lang)}")
        ui.print_message(f" [bold cyan]2.[/bold cyan] {translate('option_2_clean', lang=lang)}")
        ui.print_message(f" [bold cyan]3.[/bold cyan] {translate('option_3_clean', lang=lang)}")
        ui.print_message(f" [bold cyan]4.[/bold cyan] {translate('option_4_clean', lang=lang)}")
        ui.print_message(f" [bold cyan]5.[/bold cyan] {translate('option_5_clean', lang=lang)}")

        option = ui.ask_string(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "3", "4", "5"])

        try:
            if option == "1":
                register_day(lang=lang)
                ui.ask_string(translate('press_enter', lang=lang), default="")
            elif option == "2":
                view_history(lang=lang)
            elif option == "3":
                config_menu(lang=lang)
            elif option == "4":
                project_menu(lang=lang)
            elif option == "5":
                ui.print_message(f"\n{translate('exit_msg', lang=lang)}", style="bold blue")
                break
        except KeyboardInterrupt:
            ui.print_message(f"\n\n {translate('op_cancelled', lang=lang)} ", style="yellow")
            break


def main():
    parser = argparse.ArgumentParser(
        description="time-balance: A professional tool to track your working hours balance globally."
    )
    parser.add_argument("-s", "--status", action="store_true", help="Show only the accumulated balance.")
    parser.add_argument("-l", "--list", type=int, nargs="?", const=5, help="List last N records (default 5).")
    parser.add_argument("--version", action="store_true", help="Show application version.")
    parser.add_argument("--lang", type=str, choices=["en", "es", "auto"], default="auto", help="Force interface language.")
    parser.add_argument("--migrate", type=str, metavar="JSON_FILE", help="Migrate records from a legacy JSON file.")

    args = parser.parse_args()

    if args.version:
        ui.print_message(f"time-balance [bold cyan]v{config.VERSION}[/bold cyan]")
        return

    lang = args.lang
    if lang == "auto":
        lang = get_current_lang()

    if args.migrate:
        migrate_from_json(args.migrate, lang=lang)
        return

    active_id = db.get_active_project_id()
    project = db.get_project_by_id(active_id)

    if args.status:
        total_balance = db.get_total_balance(active_id)
        balance_fmt = format_time(total_balance)
        color = "green" if total_balance >= 0 else "red"
        if total_balance > 0: balance_fmt = f"+{balance_fmt}"
        
        ui.print_message(translate('status_project', lang=lang, name=project['name']), style="bold cyan")
        ui.print_message(translate('status_balance', lang=lang, balance=f'[{color}]{balance_fmt}[/{color}]'), style="bold")
        return

    if args.list is not None:
        view_history(limit=args.list, lang=lang)
        return

    interactive_menu()
