from ..utils.calculations import format_time
from ..ui import interface as ui
from ..utils.i18n import translate
from ..database.manager import db

def view_history(limit: int = None, lang: str = "en"):
    """Displays records for the active project. Handles both static list and interactive pagination."""
    active_id = db.get_active_project_id()
    
    if limit is not None:
        # --- Static Mode (CLI --list argument) ---
        records = db.get_records(active_id, limit=limit if limit > 0 else None)
        if not records:
            ui.print_message(f"\n{translate('no_records', lang=lang)}", style="yellow")
            return
        
        title = translate("full_history_header", lang=lang) if limit <= 0 else translate("recent_records_header", lang=lang, limit=limit)
        
        columns = [
            ("Date", {"style": "dim", "justify": "center"}),
            (translate("work_label", lang=lang), {"justify": "right"}),
            (translate("balance_short_label", lang=lang), {"justify": "right"})
        ]
        
        rows = []
        for record in records:
            time_fmt = format_time(record['difference'])
            color = "green" if record['difference'] >= 0 else "red"
            if record['difference'] > 0:
                time_fmt = f"+{time_fmt}"
            rows.append([record['date'], f"{record['hours']}h {record['minutes']}m", f"[{color}]{time_fmt}[/{color}]"])
            
        ui.render_table(title, columns, rows)
        return

    # --- Interactive Pagination Mode ---
    page_size = 10
    current_page = 0
    while True:
        total_count = db.count_records(active_id)
        if total_count == 0:
            ui.print_message(f"\n{translate('no_records', lang=lang)}", style="yellow")
            ui.ask_string(translate('press_enter', lang=lang), default="")
            break

        total_pages = (total_count + page_size - 1) // page_size
        offset = current_page * page_size
        records = db.get_records(active_id, limit=page_size, offset=offset)

        ui.clear_screen()
        title = translate("full_history_header", lang=lang)
        columns = [
            ("Date", {"style": "dim", "justify": "center"}),
            (translate("work_label", lang=lang), {"justify": "right"}),
            (translate("balance_short_label", lang=lang), {"justify": "right"})
        ]
        
        rows = []
        for record in records:
            time_fmt = format_time(record['difference'])
            color = "green" if record['difference'] >= 0 else "red"
            if record['difference'] > 0:
                time_fmt = f"+{time_fmt}"
            rows.append([record['date'], f"{record['hours']}h {record['minutes']}m", f"[{color}]{time_fmt}[/{color}]"])
        
        ui.render_table(title, columns, rows)
        ui.print_message(f"\n {translate('pagination_info', lang=lang, current=current_page+1, total=total_pages, count=total_count)}")
        
        choices = ["v"]
        nav_msg = f"\n [bold cyan]V.[/bold cyan] {translate('pagination_back', lang=lang)}"
        if current_page < total_pages - 1:
            nav_msg += f"  [bold cyan]N.[/bold cyan] {translate('pagination_next', lang=lang)}"
            choices.append("n")
        if current_page > 0:
            nav_msg += f"  [bold cyan]P.[/bold cyan] {translate('pagination_prev', lang=lang)}"
            choices.append("p")
        
        ui.print_message(nav_msg)
        choice = ui.ask_string("", default="v", choices=choices).lower()
        
        if choice == "n":
            current_page += 1
        elif choice == "p":
            current_page -= 1
        elif choice == "v":
            break
