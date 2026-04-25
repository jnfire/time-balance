import argparse
import sys
from ..utils.calculations import format_time, get_balance_color
from ..ui import interface as ui
from ..database.manager import db
from ..i18n.translator import translate, resolve_language
from .. import config

# Import sibling modules
from .registration import register_day
from .history import view_history
from .config_menu import config_menu
from .projects import project_menu
from .migration import migrate_from_json

def get_current_lang() -> str:
    """Determines the active language based on settings or system."""
    language_setting = db.get_setting("language", "auto")
    return resolve_language(language_setting)


def display_dashboard(project_data: dict, current_balance: int, lang: str):
    """Prepares and sends dashboard data to the UI interface."""
    balance_fmt = format_time(current_balance)
    balance_color = get_balance_color(current_balance)

    labels_dict = {
        'project': translate('project_label', lang=lang),
        'base_day': translate('base_day_label', lang=lang),
        'balance': translate('balance_label', lang=lang),
        'dashboard_title': translate('dashboard_title', lang=lang)
    }
    
    ui.render_dashboard(
        project_name=project_data['name'],
        base_hours=project_data['base_hours'],
        base_minutes=project_data['base_minutes'],
        balance_fmt=balance_fmt,
        balance_color=balance_color,
        version=config.VERSION,
        labels=labels_dict
    )


def interactive_menu():
    """Main interactive menu loop."""
    while True:
        current_lang = get_current_lang()
        active_project_id = db.get_active_project_id()
        current_project = db.get_project_by_id(active_project_id)
        total_project_balance = db.get_total_balance(active_project_id)

        ui.clear_screen()
        display_dashboard(current_project, total_project_balance, current_lang)

        ui.print_message(f"\n [bold blue]1.[/bold blue] {translate('option_1_clean', lang=current_lang)}")
        ui.print_message(f" [bold blue]2.[/bold blue] {translate('option_2_clean', lang=current_lang)}")
        ui.print_message(f" [bold blue]3.[/bold blue] {translate('option_3_clean', lang=current_lang)}")
        ui.print_message(f" [bold blue]4.[/bold blue] {translate('option_4_clean', lang=current_lang)}")
        ui.print_message(f" [bold blue]5.[/bold blue] {translate('option_5_clean', lang=current_lang)}")

        user_option = ui.ask_string(f"\n{translate('choose_option', lang=current_lang)}", choices=["1", "2", "3", "4", "5"])

        try:
            if user_option == "1":
                register_day(lang=current_lang)
                ui.ask_string(translate('press_enter', lang=current_lang), default="")
            elif user_option == "2":
                view_history(lang=current_lang)
            elif user_option == "3":
                config_menu(lang=current_lang)
            elif user_option == "4":
                project_menu(lang=current_lang)
            elif user_option == "5":
                ui.print_message(f"\n{translate('exit_msg', lang=current_lang)}", style="bold blue")
                break
        except KeyboardInterrupt:
            ui.print_message(f"\n\n {translate('op_cancelled', lang=current_lang)} ", style="yellow")
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
        ui.print_message(f"time-balance [bold blue]v{config.VERSION}[/bold blue]")
        return

    active_lang = args.lang
    if active_lang == "auto":
        active_lang = get_current_lang()

    if args.migrate:
        migrate_from_json(args.migrate, lang=active_lang)
        return

    active_project_id = db.get_active_project_id()
    current_project = db.get_project_by_id(active_project_id)

    if args.status:
        total_project_balance = db.get_total_balance(active_project_id)
        balance_display_fmt = format_time(total_project_balance)
        balance_display_color = get_balance_color(total_project_balance)
        
        ui.print_message(translate('status_project', lang=active_lang, name=current_project['name']), style="bold blue")
        ui.print_message(translate('status_balance', lang=active_lang, balance=f'[{balance_display_color}]{balance_display_fmt}[/{balance_display_color}]'), style="bold")
        return

    if args.list is not None:
        view_history(limit=args.list, lang=active_lang)
        return

    interactive_menu()
