import os
import sys
import argparse
from datetime import date, datetime
from . import constants
from . import core
from . import storage
from . import io
from .i18n import translate, get_system_language


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


def configure_project(data, lang="en"):
    """Configures project metadata."""
    metadata = data["metadata"]
    print(translate("config_header", lang=lang))
    
    new_name = input(translate("project_name_prompt", lang=lang, current=metadata['project_name'])).strip()
    if new_name:
        metadata["project_name"] = new_name

    try:
        hours_str = input(translate("base_hours_prompt", lang=lang, current=metadata['hours_base'])).strip()
        if hours_str:
            metadata["hours_base"] = int(hours_str)
        
        minutes_str = input(translate("base_minutes_prompt", lang=lang, current=metadata['minutes_base'])).strip()
        if minutes_str:
            metadata["minutes_base"] = int(minutes_str)
    except ValueError:
        print(translate("error_integers", lang=lang))


def register_day(data, file_path=None, lang="en"):
    """Interactive flow to register working hours."""
    work_date = request_date(lang=lang)
    metadata = data["metadata"]
    records = data["records"]

    if work_date in records:
        print(translate("duplicate_warning", lang=lang, date=work_date))
        print(translate("previous_record", lang=lang, hours=records[work_date]['hours'], minutes=records[work_date]['minutes']))
        confirmation = input(translate("overwrite_confirm", lang=lang)).lower()
        if confirmation not in ('s', 'y'):
            print(translate("op_cancelled", lang=lang))
            return

    print(translate("input_header", lang=lang, date=work_date))
    try:
        hours = int(input(translate("hours_worked", lang=lang)) or 0)
        minutes = int(input(translate("minutes_worked", lang=lang)) or 0)
    except ValueError:
        print(translate("error_integers", lang=lang))
        return

    base_minutes = (metadata["hours_base"] * 60) + metadata["minutes_base"]
    worked_minutes = (hours * 60) + minutes
    difference = worked_minutes - base_minutes

    records[work_date] = {
        "hours": hours,
        "minutes": minutes,
        "difference": difference
    }

    storage.save_data(data, file_path)
    print(translate("save_success", lang=lang, date=work_date))
    print(translate("day_diff", lang=lang, diff=core.format_time(difference)))


def view_history(data, limit=5, lang="en"):
    """Displays last records."""
    records = data["records"]
    
    if limit > 0:
        print(translate("recent_records_header", lang=lang, limit=limit))
    else:
        print(translate("full_history_header", lang=lang))
        
    sorted_dates = sorted(records.keys(), reverse=True)
    if limit > 0:
        sorted_dates = sorted_dates[:limit]
        
    if not sorted_dates:
        print(translate("no_records", lang=lang))

    for work_date in sorted_dates:
        info = records[work_date]
        time_fmt = core.format_time(info['difference'])
        if info['difference'] > 0:
            time_fmt = "+" + time_fmt

        print(f"{work_date} | Work: {info['hours']}h {info['minutes']}m | Bal: {time_fmt}")


def interactive_menu():
    """Main interactive menu loop."""
    data = storage.load_data()
    lang = data["metadata"].get("language", "auto")
    if lang == "auto":
        lang = get_system_language()

    while True:
        data = storage.load_data()
        metadata = data["metadata"]
        total_balance = core.calculate_total_balance(data["records"])

        lang = metadata.get("language", "auto")
        if lang == "auto":
            lang = get_system_language()

        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "="*50)
        print(f"   {translate('project_label', lang=lang)}: {metadata['project_name'].upper()}")
        print(f"   {translate('balance_label', lang=lang)}: {core.format_time(total_balance)}")
        print(f"   ({translate('base_day_label', lang=lang)}: {metadata['hours_base']}h {metadata['minutes_base']}m)")
        print("="*50)

        print(f"\n{translate('option_1', lang=lang)}")
        print(translate('option_2', lang=lang))
        print(translate('option_3', lang=lang))
        print(translate('option_4', lang=lang))
        print(translate('option_5', lang=lang))
        print(translate('option_6', lang=lang))

        option = input(f"\n{translate('choose_option', lang=lang)}")

        if option == "1":
            register_day(data, lang=lang)
            input(translate('press_enter', lang=lang))
        elif option == "2":
            view_history(data, lang=lang)
            input(translate('press_enter', lang=lang))
        elif option == "3":
            configure_project(data, lang=lang)
            storage.save_data(data)
            input(translate('press_enter', lang=lang))
        elif option == "4":
            path = input(translate('export_dest_prompt', lang=lang))
            try:
                dest = io.export_history(path)
                print(translate('export_success', lang=lang, path=dest))
            except Exception as err:
                print(translate('export_error', lang=lang, error=err))
            input(translate('press_enter', lang=lang))
        elif option == "5":
            path = input(translate('import_src_prompt', lang=lang))
            mode_input = input(translate('import_mode_prompt', lang=lang, merge=constants.MODE_MERGE, overwrite=constants.MODE_OVERWRITE)).strip().lower()
            mode = mode_input if mode_input else constants.MODE_MERGE
            try:
                result = io.import_history(path, mode=mode)
                print(translate('import_success', lang=lang, count=len(result['records'])))
            except Exception as err:
                print(translate('import_error', lang=lang, error=err))
            input(translate('press_enter', lang=lang))
        elif option == "6":
            print(translate('exit_msg', lang=lang))
            break


def main():
    parser = argparse.ArgumentParser(
        description="time-balance: A simple tool to track your hour balance."
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

    args = parser.parse_args()

    if args.version:
        print(f"time-balance v{constants.VERSION}")
        return

    data = storage.load_data()
    lang = args.lang
    if lang == "auto":
        lang = data["metadata"].get("language", "auto")
        if lang == "auto":
            lang = get_system_language()

    if args.status:
        total_balance = core.calculate_total_balance(data["records"])
        print(translate("status_project", lang=lang, name=data['metadata']['project_name']))
        print(translate("status_balance", lang=lang, balance=core.format_time(total_balance)))
        return

    if args.list is not None:
        view_history(data, limit=args.list, lang=lang)
        return

    interactive_menu()
