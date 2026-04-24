import os
import argparse
from datetime import date, datetime
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich import box

from . import constants
from . import core
from .storage import db
from . import io
from .i18n import translate, get_system_language

console = Console()

def get_current_lang() -> str:
    """Determines the active language based on settings or system."""
    lang = db.get_setting("language", "auto")
    if lang == "auto":
        return get_system_language()
    return lang


def render_dashboard(project: dict, balance: int, lang: str):
    """Renders a beautiful dashboard header with project info and balance."""
    balance_fmt = core.format_time(balance)
    balance_color = "green" if balance >= 0 else "red"
    if balance > 0:
        balance_fmt = f"+{balance_fmt}"

    dashboard_content = (
        f"[bold cyan]{translate('project_label', lang=lang)}:[/bold cyan] {project['name'].upper()}\n"
        f"[bold cyan]{translate('base_day_label', lang=lang)}:[/bold cyan] {project['base_hours']}h {project['base_minutes']}m\n"
        f"[bold cyan]{translate('balance_label', lang=lang)}:[/bold cyan] [{balance_color}]{balance_fmt}[/{balance_color}]"
    )
    
    panel = Panel(
        Align.center(dashboard_content),
        title=f"[bold]{translate('dashboard_title', lang=lang)}[/bold]",
        subtitle=f"v{constants.VERSION}",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)


def request_date(lang="en") -> str:
    """Requests date from user using rich prompts."""
    today = date.today().strftime("%Y-%m-%d")
    console.print(f"\n[bold yellow]{translate('date_prompt', lang=lang, today=today)}[/bold yellow]")
    
    date_input = Prompt.ask(
        translate("date_input", lang=lang),
        default=today,
        console=console
    ).strip()

    try:
        datetime.strptime(date_input, "%Y-%m-%d")
        return date_input
    except ValueError:
        console.print(f"[bold red]{translate('invalid_date', lang=lang)}[/bold red]")
        return today


def register_day(lang="en"):
    """Interactive flow to register working hours for the active project."""
    active_id = db.get_active_project_id()
    project = db.get_project_by_id(active_id)
    work_date = request_date(lang=lang)

    existing_record = db.get_record_by_date(active_id, work_date)
    if existing_record:
        console.print(f"\n[bold yellow]{translate('duplicate_warning', lang=lang, date=work_date)}[/bold yellow]")
        console.print(f"   {translate('previous_record', lang=lang, hours=existing_record['hours'], minutes=existing_record['minutes'])}")
        
        if not Confirm.ask(translate("overwrite_confirm", lang=lang), default=False, console=console):
            console.print(f"[blue]{translate('op_cancelled', lang=lang)}[/blue]")
            return

    console.print(f"\n[bold cyan]{translate('input_header', lang=lang, date=work_date)}[/bold cyan]")
    try:
        hours = int(Prompt.ask(translate("hours_worked", lang=lang), default="0", console=console))
        minutes = int(Prompt.ask(translate("minutes_worked", lang=lang), default="0", console=console))
    except ValueError:
        console.print(f"[bold red]{translate('error_integers', lang=lang)}[/bold red]")
        return

    base_minutes = (project["base_hours"] * 60) + project["base_minutes"]
    worked_minutes = (hours * 60) + minutes
    difference = worked_minutes - base_minutes

    db.upsert_record(active_id, work_date, hours, minutes, difference)

    console.print(f"\n[bold green]{translate('save_success', lang=lang, date=work_date)}[/bold green]")
    console.print(f"   {translate('day_diff', lang=lang, diff=core.format_time(difference))}")


def view_history(limit=None, lang="en"):
    """Displays records for the active project. If limit is None, it enters interactive pagination."""
    active_id = db.get_active_project_id()
    
    if limit is not None:
        # Static mode for CLI --list argument
        records = db.get_records(active_id, limit=limit if limit > 0 else None)
        if not records:
            console.print(f"\n[yellow]{translate('no_records', lang=lang)}[/yellow]")
            return
        
        title = translate("full_history_header", lang=lang) if limit <= 0 else translate("recent_records_header", lang=lang, limit=limit)
        table = Table(title=f"\n[bold]{title}[/bold]", box=box.SIMPLE_HEAD, header_style="bold cyan")
        table.add_column("Date", style="dim", justify="center")
        table.add_column(translate("work_label", lang=lang), justify="right")
        table.add_column(translate("balance_short_label", lang=lang), justify="right")

        for record in records:
            time_fmt = core.format_time(record['difference'])
            color = "green" if record['difference'] >= 0 else "red"
            if record['difference'] > 0:
                time_fmt = f"+{time_fmt}"
            table.add_row(record['date'], f"{record['hours']}h {record['minutes']}m", f"[{color}]{time_fmt}[/{color}]")
        console.print(table)
        return

    # Interactive Pagination mode
    page_size = 10
    current_page = 0
    while True:
        total_count = db.count_records(active_id)
        if total_count == 0:
            console.print(f"\n[yellow]{translate('no_records', lang=lang)}[/yellow]")
            Prompt.ask(translate('press_enter', lang=lang), console=console)
            break

        total_pages = (total_count + page_size - 1) // page_size
        offset = current_page * page_size
        records = db.get_records(active_id, limit=page_size, offset=offset)

        console.clear()
        title = translate("full_history_header", lang=lang)
        table = Table(title=f"\n[bold]{title}[/bold]", box=box.SIMPLE_HEAD, header_style="bold cyan")
        table.add_column("Date", style="dim", justify="center")
        table.add_column(translate("work_label", lang=lang), justify="right")
        table.add_column(translate("balance_short_label", lang=lang), justify="right")

        for record in records:
            time_fmt = core.format_time(record['difference'])
            color = "green" if record['difference'] >= 0 else "red"
            if record['difference'] > 0:
                time_fmt = f"+{time_fmt}"
            
            table.add_row(
                record['date'],
                f"{record['hours']}h {record['minutes']}m",
                f"[{color}]{time_fmt}[/{color}]"
            )
        
        console.print(table)
        console.print(f"\n {translate('pagination_info', lang=lang, current=current_page+1, total=total_pages, count=total_count)}")
        
        choices = ["v"]
        nav_msg = f"\n [bold cyan]V.[/bold cyan] {translate('pagination_back', lang=lang)}"
        if current_page < total_pages - 1:
            nav_msg += f"  [bold cyan]N.[/bold cyan] {translate('pagination_next', lang=lang)}"
            choices.append("n")
        if current_page > 0:
            nav_msg += f"  [bold cyan]P.[/bold cyan] {translate('pagination_prev', lang=lang)}"
            choices.append("p")
        
        console.print(nav_msg)
        choice = Prompt.ask("", choices=choices, show_choices=False, console=console).lower()
        
        if choice == "n":
            current_page += 1
        elif choice == "p":
            current_page -= 1
        elif choice == "v":
            break


def config_menu(lang="en"):
    """Submenu for project-specific and global configuration."""
    while True:
        active_id = db.get_active_project_id()
        project = db.get_project_by_id(active_id)
        
        console.clear()
        console.print(f"\n[bold cyan]--- {translate('option_3_clean', lang=lang).upper()} ---[/bold cyan]")
        
        # Display current configuration
        console.print(f"\n [dim]{translate('project_label', lang=lang)}:[/dim] [bold]{project['name']}[/bold]")
        console.print(f" [dim]{translate('base_day_label', lang=lang)}:[/dim] [bold]{project['base_hours']}h {project['base_minutes']}m[/bold]")
        console.print(f" [dim]Language:[/dim] [bold]{db.get_setting('language', 'auto')}[/bold]")
        
        console.print(f"\n[bold dim]>> {translate('config_section_project', lang=lang)}[/bold dim]")
        console.print(f" [bold cyan]1.[/bold cyan] {translate('config_option_edit_name', lang=lang)}")
        console.print(f" [bold cyan]2.[/bold cyan] {translate('config_option_edit_base', lang=lang)}")
        console.print(f" [bold cyan]3.[/bold cyan] {translate('config_option_lang', lang=lang)}")
        
        console.print(f"\n[bold dim]>> {translate('config_section_data', lang=lang)}[/bold dim]")
        console.print(f" [bold cyan]4.[/bold cyan] {translate('config_option_import', lang=lang)}")
        console.print(f" [bold cyan]5.[/bold cyan] {translate('config_option_export', lang=lang)}")
        
        console.print(f"\n [bold cyan]V.[/bold cyan] {translate('config_option_back', lang=lang)}")
        
        choice = Prompt.ask(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "3", "4", "5", "v"], show_choices=False, console=console).lower()
        
        if choice == "1":
            new_name = Prompt.ask(translate("project_name_prompt", lang=lang, current=project['name']), default=project['name'], console=console).strip()
            if new_name:
                db.update_project(active_id, new_name, project['base_hours'], project['base_minutes'])
        elif choice == "2":
            try:
                h = int(Prompt.ask(translate("base_hours_prompt", lang=lang, current=project['base_hours']), default=str(project['base_hours']), console=console))
                m = int(Prompt.ask(translate("base_minutes_prompt", lang=lang, current=project['base_minutes']), default=str(project['base_minutes']), console=console))
                db.update_project(active_id, project['name'], h, m)
            except ValueError:
                console.print(f"[bold red]{translate('error_integers', lang=lang)}[/bold red]")
                Prompt.ask(translate("press_enter", lang=lang), console=console)
        elif choice == "3":
            lang_opt = Prompt.ask(
                translate("language_prompt", lang=lang, current=db.get_setting("language", "auto")),
                choices=["en", "es", "auto"],
                default="auto",
                console=console
            ).strip().lower()
            db.set_setting("language", lang_opt)
            # Update local lang for immediate feedback
            lang = lang_opt if lang_opt != "auto" else get_system_language()
        elif choice == "4":
            path = Prompt.ask(translate('import_src_prompt', lang=lang), console=console).strip()
            if path:
                mode = Prompt.ask(
                    translate('import_mode_prompt', lang=lang, merge=constants.MODE_MERGE, overwrite=constants.MODE_OVERWRITE),
                    choices=[constants.MODE_MERGE, constants.MODE_OVERWRITE],
                    default=constants.MODE_MERGE,
                    console=console
                )
                try:
                    source_data = io.read_history_file(path)
                    
                    if mode == constants.MODE_OVERWRITE:
                        db.clear_project_records(active_id)
                    else:
                        # Only reset cache if merging (overwrite already sets balance to 0)
                        db.reset_project_balance(active_id)
                    
                    count = 0

                    for date_str, info in source_data['records'].items():
                        db.upsert_record(active_id, date_str, info['hours'], info['minutes'], info['difference'])
                        count += 1
                    console.print(f"[bold green]{translate('import_success', lang=lang, count=count)}[/bold green]")
                except Exception as err:
                    console.print(f"[bold red]{translate('import_error', lang=lang, error=err)}[/bold red]")
                Prompt.ask(translate('press_enter', lang=lang), console=console)
        elif choice == "5":
            path = Prompt.ask(translate('export_dest_prompt', lang=lang), console=console).strip()
            if path:
                try:
                    records = db.get_records(active_id)
                    data_to_export = {
                        "metadata": {
                            "project_name": project['name'],
                            "hours_base": project['base_hours'],
                            "minutes_base": project['base_minutes'],
                            "version": "1.0",
                            "language": db.get_setting("language", "auto")
                        },
                        "records": {r['date']: {'hours': r['hours'], 'minutes': r['minutes'], 'difference': r['difference']} for r in records}
                    }
                    dest = io.export_history(data_to_export, path)
                    console.print(f"[bold green]{translate('export_success', lang=lang, path=dest)}[/bold green]")
                except Exception as err:
                    console.print(f"[bold red]{translate('export_error', lang=lang, error=err)}[/bold red]")
                Prompt.ask(translate('press_enter', lang=lang), console=console)
        elif choice == "v":
            break


def project_menu(lang="en"):
    """Submenu for switching and creating projects."""
    while True:
        projects = db.get_projects()
        active_id = db.get_active_project_id()

        console.clear()
        console.print(f"\n[bold cyan]--- {translate('option_4_clean', lang=lang).upper()} ---[/bold cyan]")
        
        table = Table(box=box.SIMPLE, header_style="bold dim")
        table.add_column("ID", justify="center", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Base", justify="center", style="dim")
        table.add_column("Active", justify="center")

        for p in projects:
            is_active = "[bold cyan]●[/bold cyan]" if p['id'] == active_id else ""
            table.add_row(str(p['id']), p['name'], f"{p['base_hours']}h {p['base_minutes']}m", is_active)
        
        console.print(table)
            
        console.print(f"\n [bold cyan]1.[/bold cyan] {translate('project_option_select', lang=lang)}")
        console.print(f" [bold cyan]2.[/bold cyan] {translate('project_option_create', lang=lang)}")
        console.print(f"\n [bold cyan]V.[/bold cyan] {translate('project_option_back', lang=lang)}")
        
        choice = Prompt.ask(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "v"], show_choices=False, console=console).lower()
        
        if choice == "1":
            target_id = Prompt.ask(translate("enter_project_id", lang=lang), console=console)
            if target_id.isdigit() and any(p['id'] == int(target_id) for p in projects):
                db.set_active_project_id(int(target_id))
                break
            else:
                console.print(f"[bold red]{translate('invalid_option', lang=lang)}[/bold red]")
                Prompt.ask(translate("press_enter", lang=lang), console=console)
        elif choice == "2":
            name = Prompt.ask(translate("project_name_prompt", lang=lang, current="New"), console=console).strip()
            if name:
                try:
                    h = int(Prompt.ask(translate("base_hours_prompt", lang=lang, current=constants.BASE_HOURS), default=str(constants.BASE_HOURS), console=console))
                    m = int(Prompt.ask(translate("base_minutes_prompt", lang=lang, current=constants.BASE_MINUTES), default=str(constants.BASE_MINUTES), console=console))
                    new_id = db.create_project(name, h, m)
                    db.set_active_project_id(new_id)
                    break
                except ValueError:
                    console.print(f"[bold red]{translate('error_integers', lang=lang)}[/bold red]")
                    Prompt.ask(translate("press_enter", lang=lang), console=console)
        elif choice == "v":
            break


def interactive_menu():
    """Main interactive menu loop with a clean, sober layout."""
    while True:
        lang = get_current_lang()
        active_id = db.get_active_project_id()
        project = db.get_project_by_id(active_id)
        total_balance = db.get_total_balance(active_id)

        console.clear()
        render_dashboard(project, total_balance, lang)

        console.print(f"\n [bold cyan]1.[/bold cyan] {translate('option_1_clean', lang=lang)}")
        console.print(f" [bold cyan]2.[/bold cyan] {translate('option_2_clean', lang=lang)}")
        console.print(f" [bold cyan]3.[/bold cyan] {translate('option_3_clean', lang=lang)}")
        console.print(f" [bold cyan]4.[/bold cyan] {translate('option_4_clean', lang=lang)}")
        console.print(f" [bold cyan]5.[/bold cyan] {translate('option_5_clean', lang=lang)}")

        option = Prompt.ask(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "3", "4", "5"], show_choices=False, console=console)

        try:
            if option == "1":
                register_day(lang=lang)
                Prompt.ask(translate('press_enter', lang=lang), console=console)
            elif option == "2":
                view_history(lang=lang)
            elif option == "3":
                config_menu(lang=lang)
            elif option == "4":
                project_menu(lang=lang)
            elif option == "5":
                console.print(f"\n[bold blue]{translate('exit_msg', lang=lang)}[/bold blue]")
                break
        except KeyboardInterrupt:
            console.print(f"\n\n[yellow] {translate('op_cancelled', lang=lang)} [/yellow]")
            break


def migrate_from_json(path: str, lang: str):
    """Migrates records from a legacy JSON file to the SQLite database."""
    try:
        source_data = io.read_history_file(path)
        metadata = source_data.get("metadata", {})
        
        console.print(f"\n[bold cyan]{translate('import_header', lang=lang, date=path)}[/bold cyan]")
        
        # 1. Create the project
        project_name = metadata.get("project_name", f"Imported {date.today()}")
        h = metadata.get("hours_base", constants.BASE_HOURS)
        m = metadata.get("minutes_base", constants.BASE_MINUTES)
        
        new_id = db.create_project(project_name, h, m)
        db.set_active_project_id(new_id)
        
        # 2. Insert records
        count = 0
        records = source_data.get("records", {})
        for date_str, info in records.items():
            db.upsert_record(new_id, date_str, info['hours'], info['minutes'], info['difference'])
            count += 1
            
        console.print(f"[bold green]{translate('import_success', lang=lang, count=count)}[/bold green]")
        console.print(f"   {translate('project_label', lang=lang)}: [bold]{project_name}[/bold] (ID: {new_id})")
        
    except Exception as err:
        console.print(f"[bold red]{translate('import_error', lang=lang, error=err)}[/bold red]")


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
        console.print(f"time-balance [bold cyan]v{constants.VERSION}[/bold cyan]")
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
        balance_fmt = core.format_time(total_balance)
        color = "green" if total_balance >= 0 else "red"
        if total_balance > 0: balance_fmt = f"+{balance_fmt}"
        
        console.print(f"[bold cyan]{translate('status_project', lang=lang, name=project['name'])}[/bold cyan]")
        console.print(f"[bold]{translate('status_balance', lang=lang, balance=f'[{color}]{balance_fmt}[/{color}]')}[/bold]")
        return

    if args.list is not None:
        view_history(limit=args.list, lang=lang)
        return

    interactive_menu()
