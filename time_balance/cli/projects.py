from ..ui import interface as ui
from ..utils.i18n import translate
from ..database.manager import db
from .. import config

def project_menu(lang: str = "en"):
    """Submenu for switching and creating projects."""
    while True:
        projects = db.get_projects()
        active_id = db.get_active_project_id()

        ui.clear_screen()
        ui.print_message(f"\n--- {translate('option_4_clean', lang=lang).upper()} ---", style="bold cyan")
        
        columns = [
            ("ID", {"justify": "center", "style": "dim"}),
            ("Name", {"style": "bold"}),
            ("Base", {"justify": "center", "style": "dim"}),
            ("Active", {"justify": "center"})
        ]
        
        rows = []
        for p in projects:
            is_active = "[bold cyan]●[/bold cyan]" if p['id'] == active_id else ""
            rows.append([str(p['id']), p['name'], f"{p['base_hours']}h {p['base_minutes']}m", is_active])
        
        ui.render_simple_table(columns, rows)
            
        ui.print_message(f"\n [bold cyan]1.[/bold cyan] {translate('project_option_select', lang=lang)}")
        ui.print_message(f" [bold cyan]2.[/bold cyan] {translate('project_option_create', lang=lang)}")
        ui.print_message(f"\n [bold cyan]V.[/bold cyan] {translate('project_option_back', lang=lang)}")
        
        choice = ui.ask_string(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "v"]).lower()
        
        if choice == "1":
            target_id = ui.ask_string(translate("enter_project_id", lang=lang))
            if target_id.isdigit() and any(p['id'] == int(target_id) for p in projects):
                db.set_active_project_id(int(target_id))
                break
            else:
                ui.print_message(translate('invalid_option', lang=lang), style="bold red")
                ui.ask_string(translate("press_enter", lang=lang), default="")
        elif choice == "2":
            name = ui.ask_string(translate("project_name_prompt", lang=lang, current="New")).strip()
            if name:
                try:
                    h = int(ui.ask_string(translate("base_hours_prompt", lang=lang, current=config.BASE_HOURS), default=str(config.BASE_HOURS)))
                    m = int(ui.ask_string(translate("base_minutes_prompt", lang=lang, current=config.BASE_MINUTES), default=str(config.BASE_MINUTES)))
                    new_id = db.create_project(name, h, m)
                    db.set_active_project_id(new_id)
                    break
                except ValueError:
                    ui.print_message(translate('error_integers', lang=lang), style="bold red")
                    ui.ask_string(translate("press_enter", lang=lang), default="")
        elif choice == "v":
            break
