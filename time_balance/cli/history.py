from typing import List, Dict, Any
from ..utils.calculations import format_time, get_balance_color
from ..ui import interface as ui
from ..i18n.translator import translate
from ..database.manager import db

def _prepare_table_rows(records_list: List[Dict[str, Any]]) -> List[List[str]]:
    """Helper to format database records into displayable table rows."""
    formatted_rows = []
    for record in records_list:
        difference_value = record['difference']
        time_balance_fmt = format_time(difference_value)
        row_color = get_balance_color(difference_value)
        
        formatted_rows.append([
            record['date'], 
            f"{record['hours']}h {record['minutes']}m", 
            f"[{row_color}]{time_balance_fmt}[/{row_color}]"
        ])
    return formatted_rows


def _delete_record_flow(active_project_id: int, lang: str):
    """Handles the workflow for deleting a record: show list, date input, confirmation, and deletion."""
    table_columns = [
        ("Date", {"style": "dim", "justify": "center"}),
        (translate("work_label", lang=lang), {"justify": "right"}),
        (translate("balance_short_label", lang=lang), {"justify": "right"})
    ]
    
    # Fetch recent records for reference
    paged_records = db.get_records(active_project_id, limit=10)
    if not paged_records:
        ui.clear_screen()
        ui.print_message(f"\n{translate('no_records', lang=lang)}", style="yellow")
        ui.ask_string(translate('press_enter', lang=lang), default="")
        return
    
    # Display the records table for reference
    ui.clear_screen()
    ui.render_header(translate("delete_record_option", lang=lang))
    display_rows = _prepare_table_rows(paged_records)
    ui.render_table("", table_columns, display_rows)
    
    # Request the exact date to delete
    ui.print_message("")
    user_date_input = ui.ask_string(translate("delete_date_prompt", lang=lang), default="")
    
    if not user_date_input.strip():
        ui.print_message(translate("op_cancelled", lang=lang), style="yellow")
        ui.ask_string(translate('press_enter', lang=lang), default="")
        return
    
    # Fetch the record
    record_to_delete = db.get_record_by_date(active_project_id, user_date_input)
    
    if not record_to_delete:
        ui.print_message(
            translate("delete_record_not_found", lang=lang, date=user_date_input),
            style="red"
        )
        ui.ask_string(translate('press_enter', lang=lang), default="")
        return
    
    # Show confirmation with record details
    difference_fmt = format_time(record_to_delete['difference'])
    confirmation_message = translate(
        "delete_record_confirm",
        lang=lang,
        date=record_to_delete['date'],
        hours=record_to_delete['hours'],
        minutes=record_to_delete['minutes'],
        diff=difference_fmt
    )
    
    user_confirmation = ui.ask_string(confirmation_message, choices=["s", "n"] if lang == "es" else ["y", "n"])
    
    if user_confirmation.lower() not in ("s", "y"):
        ui.print_message(translate("op_cancelled", lang=lang), style="yellow")
        ui.ask_string(translate('press_enter', lang=lang), default="")
        return
    
    # Delete the record
    db.delete_record(active_project_id, record_to_delete['date'])
    ui.print_message(
        translate("delete_success", lang=lang, date=record_to_delete['date']),
        style="green"
    )
    ui.ask_string(translate('press_enter', lang=lang), default="")



def view_history(limit: int = None, lang: str = "en"):
    """Displays records for the active project. Handles both static list and interactive pagination."""
    active_project_id = db.get_active_project_id()
    
    table_columns = [
        ("Date", {"style": "dim", "justify": "center"}),
        (translate("work_label", lang=lang), {"justify": "right"}),
        (translate("balance_short_label", lang=lang), {"justify": "right"})
    ]

    if limit is not None:
        # --- Static Mode (CLI --list argument) ---
        history_records = db.get_records(active_project_id, limit=limit if limit > 0 else None)
        if not history_records:
            ui.print_message(f"\n{translate('no_records', lang=lang)}", style="yellow")
            return
        
        table_title = translate("full_history_header", lang=lang) if limit <= 0 else translate("recent_records_header", lang=lang, limit=limit)
        display_rows = _prepare_table_rows(history_records)
            
        ui.render_header(table_title)
        ui.render_table("", table_columns, display_rows)
        return

    # --- Interactive Pagination Mode ---
    page_size_limit = 10
    current_page_index = 0
    while True:
        total_records_count = db.count_records(active_project_id)
        if total_records_count == 0:
            ui.print_message(f"\n{translate('no_records', lang=lang)}", style="yellow")
            ui.ask_string(translate('press_enter', lang=lang), default="")
            break

        total_pages_count = (total_records_count + page_size_limit - 1) // page_size_limit
        offset_value = current_page_index * page_size_limit
        paged_records = db.get_records(active_project_id, limit=page_size_limit, offset=offset_value)

        ui.clear_screen()
        table_title = translate("full_history_header", lang=lang)
        display_rows = _prepare_table_rows(paged_records)
        
        ui.render_header(table_title)
        ui.render_table("", table_columns, display_rows)
        ui.print_message(f"\n {translate('pagination_info', lang=lang, current=current_page_index+1, total=total_pages_count, count=total_records_count)}")
        
        # Build navigation options
        nav_options = [("V", translate("pagination_back", lang=lang))]
        nav_choices = ["v"]
        
        if current_page_index < total_pages_count - 1:
            nav_options.append(("N", translate("pagination_next", lang=lang)))
            nav_choices.append("n")
        if current_page_index > 0:
            nav_options.append(("P", translate("pagination_prev", lang=lang)))
            nav_choices.append("p")
        
        nav_options.append(("D", translate("delete_record_option", lang=lang)))
        nav_choices.append("d")
        
        ui.render_navigation_help(nav_options)
        
        user_navigation_choice = ui.ask_string(
            translate('choose_option', lang=lang), 
            default="v", 
            choices=nav_choices
        ).lower()
        
        if user_navigation_choice == "n":
            current_page_index += 1
        elif user_navigation_choice == "p":
            current_page_index -= 1
        elif user_navigation_choice == "d":
            _delete_record_flow(active_project_id, lang)
        elif user_navigation_choice == "v":
            break
