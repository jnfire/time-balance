from typing import List, Dict, Any
from ..utils.calculations import format_time
from ..ui import interface as ui
from ..i18n.translator import translate
from ..database.manager import db

def _prepare_table_rows(records_list: List[Dict[str, Any]]) -> List[List[str]]:
    """Helper to format database records into displayable table rows."""
    formatted_rows = []
    for record in records_list:
        time_balance_fmt = format_time(record['difference'])
        row_color = "green" if record['difference'] >= 0 else "red"
        if record['difference'] > 0:
            time_balance_fmt = f"+{time_balance_fmt}"
        
        formatted_rows.append([
            record['date'], 
            f"{record['hours']}h {record['minutes']}m", 
            f"[{row_color}]{time_balance_fmt}[/{row_color}]"
        ])
    return formatted_rows


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
            
        ui.render_table(table_title, table_columns, display_rows)
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
        
        ui.render_table(table_title, table_columns, display_rows)
        ui.print_message(f"\n {translate('pagination_info', lang=lang, current=current_page_index+1, total=total_pages_count, count=total_records_count)}")
        
        navigation_choices = ["v"]
        navigation_msg = f"\n [bold cyan]V.[/bold cyan] {translate('pagination_back', lang=lang)}"
        if current_page_index < total_pages_count - 1:
            navigation_msg += f"  [bold cyan]N.[/bold cyan] {translate('pagination_next', lang=lang)}"
            navigation_choices.append("n")
        if current_page_index > 0:
            navigation_msg += f"  [bold cyan]P.[/bold cyan] {translate('pagination_prev', lang=lang)}"
            navigation_choices.append("p")
        
        ui.print_message(navigation_msg)
        user_navigation_choice = ui.ask_string(
            translate('choose_option', lang=lang), 
            default="v", 
            choices=navigation_choices
        ).lower()
        
        if user_navigation_choice == "n":
            current_page_index += 1
        elif user_navigation_choice == "p":
            current_page_index -= 1
        elif user_navigation_choice == "v":
            break
