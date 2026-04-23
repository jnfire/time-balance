import os
import argparse
from datetime import date, datetime
from . import constants
from . import core
from .storage import db
from . import io
from .i18n import translate, get_system_language


def get_current_lang():
    """Determines the active language based on settings or system."""
    lang = db.get_setting("language", "auto")
    if lang == "auto":
        return get_system_language()
    return lang


def request_date(lang="en"):
    """Requests date from user or uses today's as default."""
    today = date.today().strftime("%Y-%m-%d")
    print(translate("date_prompt", lang=lang, today=today))
    date_input = input(translate("date_input", lang=lang)).strip()

    if not date_input:
        return today

    try:
        datetime.strptime(date_input, "%Y-%m-%d")
        return date_input
    except ValueError:
        print(translate("invalid_date", lang=lang))
        return today


def register_day(lang="en"):
    """Interactive flow to register working hours for the active project."""
    active_id = db.get_active_project_id()
    project = db.get_project_by_id(active_id)
    work_date = request_date(lang=lang)

    existing_record = db.get_record_by_date(active_id, work_date)
    if existing_record:
        print(translate("duplicate_warning", lang=lang, date=work_date))
        print(translate("previous_record", lang=lang, hours=existing_record['hours'], minutes=existing_record['minutes']))
        confirmation = input(translate("overwrite_confirm", lang=lang)).lower()
        if confirmation not in ('s', 'y'):
            print(translate("op_cancelled", lang=lang))
            return

    print(translate("input_header", lang=lang, date=work_date))
    try:
        hours_input = input(translate("hours_worked", lang=lang)).strip()
        hours = int(hours_input) if hours_input else 0
        
        minutes_input = input(translate("minutes_worked", lang=lang)).strip()
        minutes = int(minutes_input) if minutes_input else 0
    except ValueError:
        print(translate("error_integers", lang=lang))
        return

    base_minutes = (project["base_hours"] * 60) + project["base_minutes"]
    worked_minutes = (hours * 60) + minutes
    difference = worked_minutes - base_minutes

    db.upsert_record(active_id, work_date, hours, minutes, difference)

    print(translate("save_success", lang=lang, date=work_date))
    print(translate("day_diff", lang=lang, diff=core.format_time(difference)))


def view_history(limit=5, lang="en"):
    """Displays last records for the active project."""
    active_id = db.get_active_project_id()
    records = db.get_records(active_id, limit=limit if limit > 0 else None)
    
    if limit > 0:
        print(translate("recent_records_header", lang=lang, limit=limit))
    else:
        print(translate("full_history_header", lang=lang))
        
    if not records:
        print(translate("no_records", lang=lang))
        return

    work_label = translate("work_label", lang=lang)
    bal_label = translate("balance_short_label", lang=lang)

    for record in records:
        time_fmt = core.format_time(record['difference'])
        if record['difference'] > 0:
            time_fmt = "+" + time_fmt
        print(f"{record['date']} | {work_label}: {record['hours']}h {record['minutes']}m | {bal_label}: {time_fmt}")


def manage_projects(lang="en"):
    """Submenu for multi-project management."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n--- {translate('projects_menu_header', lang=lang)} ---")
        projects = db.get_projects()
        active_id = db.get_active_project_id()
        
        for p in projects:
            marker = " [*]" if p['id'] == active_id else ""
            print(f"{p['id']}. {p['name']} ({p['base_hours']}h {p['base_minutes']}m){marker}")
            
        print(f"\n{translate('switch_project', lang=lang)}")
        print(translate('create_project', lang=lang))
        print(translate('edit_project', lang=lang))
        print(translate('back', lang=lang))
        
        choice = input(f"\n{translate('choose_option', lang=lang)}").strip()
        
        if choice == "1":
            target_id = input(translate("enter_project_id", lang=lang)).strip()
            if target_id.isdigit() and any(p['id'] == int(target_id) for p in projects):
                db.set_active_project_id(int(target_id))
            else:
                print(translate("invalid_option", lang=lang))
                input(translate("press_enter", lang=lang))
        elif choice == "2":
            name = input(translate("project_name_prompt", lang=lang, current="New")).strip()
            if name:
                try:
                    h = int(input(translate("base_hours_prompt", lang=lang, current=constants.BASE_HOURS)) or constants.BASE_HOURS)
                    m = int(input(translate("base_minutes_prompt", lang=lang, current=constants.BASE_MINUTES)) or constants.BASE_MINUTES)
                    new_id = db.create_project(name, h, m)
                    db.set_active_project_id(new_id)
                except ValueError:
                    print(translate("error_integers", lang=lang))
                    input(translate("press_enter", lang=lang))
        elif choice == "3":
            p = db.get_project_by_id(active_id)
            name = input(translate("project_name_prompt", lang=lang, current=p['name'])).strip() or p['name']
            try:
                h_input = input(translate("base_hours_prompt", lang=lang, current=p['base_hours'])).strip()
                h = int(h_input) if h_input else p['base_hours']
                
                m_input = input(translate("base_minutes_prompt", lang=lang, current=p['base_minutes'])).strip()
                m = int(m_input) if m_input else p['base_minutes']
                
                db.update_project(active_id, name, h, m)
                
                lang_opt = input(translate("language_prompt", lang=lang, current=db.get_setting("language", "auto"))).strip().lower()
                if lang_opt in ("en", "es", "auto"):
                    db.set_setting("language", lang_opt)
                    lang = get_current_lang()
            except ValueError:
                print(translate("error_integers", lang=lang))
                input(translate("press_enter", lang=lang))
        elif choice == "4":
            break


def migrate_from_json(file_path, lang="en"):
    """Migrates records from a legacy JSON file to a new SQLite project."""
    try:
        source_data = io.read_history_file(file_path)
        records = source_data.get("records", {})
        metadata = source_data.get("metadata", {})
        
        name = metadata.get('project_name', f"Migrated_{datetime.now().strftime('%Y%m%d')}")
        try:
            project_id = db.create_project(
                name, 
                metadata.get('hours_base', constants.BASE_HOURS),
                metadata.get('minutes_base', constants.BASE_MINUTES)
            )
        except Exception: 
            # If name exists (e.g. General), use active project
            project_id = db.get_active_project_id()
            name = db.get_project_by_id(project_id)['name']
            
        count = 0
        for date_str, info in records.items():
            db.upsert_record(project_id, date_str, info['hours'], info['minutes'], info['difference'])
            count += 1
            
        print(translate("migration_success", lang=lang, count=count, name=name))
    except Exception as e:
        print(translate("migration_error", lang=lang, error=str(e)))


def interactive_menu():
    """Main interactive menu loop."""
    while True:
        lang = get_current_lang()
        active_id = db.get_active_project_id()
        project = db.get_project_by_id(active_id)
        total_balance = db.get_total_balance(active_id)

        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "="*50)
        print(f"   {translate('project_label', lang=lang)}: {project['name'].upper()}")
        print(f"   {translate('balance_label', lang=lang)}: {core.format_time(total_balance)}")
        print(f"   ({translate('base_day_label', lang=lang)}: {project['base_hours']}h {project['base_minutes']}m)")
        print("="*50)

        print(f"\n{translate('option_1', lang=lang)}")
        print(translate('option_2', lang=lang))
        print(translate('option_3', lang=lang))
        print(translate('option_4', lang=lang))
        print(translate('option_5', lang=lang))
        print(translate('option_6', lang=lang))

        option = input(f"\n{translate('choose_option', lang=lang)}").strip()

        if option == "1":
            register_day(lang=lang)
            input(translate('press_enter', lang=lang))
        elif option == "2":
            view_history(lang=lang)
            input(translate('press_enter', lang=lang))
        elif option == "3":
            manage_projects(lang=lang)
        elif option == "4":
            path = input(translate('export_dest_prompt', lang=lang)).strip()
            if path:
                try:
                    # Convert DB data back to JSON-like structure for export
                    project_data = db.get_project_by_id(active_id)
                    records = db.get_records(active_id)
                    data_to_export = {
                        "metadata": {
                            "project_name": project_data['name'],
                            "hours_base": project_data['base_hours'],
                            "minutes_base": project_data['base_minutes'],
                            "version": "1.0",
                            "language": db.get_setting("language", "auto")
                        },
                        "records": {r['date']: {'hours': r['hours'], 'minutes': r['minutes'], 'difference': r['difference']} for r in records}
                    }
                    dest = io.export_history(data_to_export, path)
                    print(translate('export_success', lang=lang, path=dest))
                except Exception as err:
                    print(translate('export_error', lang=lang, error=err))
                input(translate('press_enter', lang=lang))
        elif option == "5":
            path = input(translate('import_src_prompt', lang=lang)).strip()
            if path:
                mode_input = input(translate('import_mode_prompt', lang=lang, merge=constants.MODE_MERGE, overwrite=constants.MODE_OVERWRITE)).strip().lower()
                mode = mode_input if mode_input else constants.MODE_MERGE
                try:
                    source_data = io.read_history_file(path)
                    
                    if mode == constants.MODE_OVERWRITE:
                        # Clear existing records for this project if overwriting
                        with db._get_connection() as conn:
                            conn.execute("DELETE FROM records WHERE project_id = ?", (active_id,))
                    
                    count = 0
                    for date_str, info in source_data['records'].items():
                        db.upsert_record(active_id, date_str, info['hours'], info['minutes'], info['difference'])
                        count += 1
                    print(translate('import_success', lang=lang, count=count))
                except Exception as err:
                    print(translate('import_error', lang=lang, error=err))
                input(translate('press_enter', lang=lang))
        elif option == "6":
            print(translate('exit_msg', lang=lang))
            break


def main():
    parser = argparse.ArgumentParser(
        description="time-balance: A professional tool to track your working hours balance globally."
    )
    parser.add_argument(
        "-s", "--status", action="store_true", help="Show only the accumulated balance."
    )
    parser.add_argument(
        "-l", "--list", type=int, nargs="?", const=5, help="List last N records (default 5)."
    )
    parser.add_argument(
        "--version", action="store_true", help="Show application version."
    )
    parser.add_argument(
        "--lang", type=str, choices=["en", "es", "auto"], default="auto", help="Force interface language."
    )
    parser.add_argument(
        "--migrate", type=str, metavar="JSON_FILE", help="Migrate records from a legacy JSON file."
    )

    args = parser.parse_args()

    if args.version:
        print(f"time-balance v{constants.VERSION}")
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
        print(translate("status_project", lang=lang, name=project['name']))
        print(translate("status_balance", lang=lang, balance=core.format_time(total_balance)))
        return

    if args.list is not None:
        view_history(limit=args.list, lang=lang)
        return

    interactive_menu()
