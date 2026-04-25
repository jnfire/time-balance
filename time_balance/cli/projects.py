from ..ui import interface as ui
from ..utils.i18n import translate
from ..database.manager import db
from .. import config

def project_menu(lang: str = "en"):
    """Submenu for switching and creating projects."""
    while True:
        projects_list = db.get_projects()
        active_project_id = db.get_active_project_id()

        ui.clear_screen()
        ui.print_message(f"\n--- {translate('option_4_clean', lang=lang).upper()} ---", style="bold cyan")
        
        table_columns = [
            ("ID", {"justify": "center", "style": "dim"}),
            ("Name", {"style": "bold"}),
            ("Base", {"justify": "center", "style": "dim"}),
            ("Active", {"justify": "center"})
        ]
        
        table_rows = []
        for project in projects_list:
            is_active_marker = "[bold cyan]●[/bold cyan]" if project['id'] == active_project_id else ""
            table_rows.append([
                str(project['id']), 
                project['name'], 
                f"{project['base_hours']}h {project['base_minutes']}m", 
                is_active_marker
            ])
        
        ui.render_simple_table(table_columns, table_rows)
            
        ui.print_message(f"\n [bold cyan]1.[/bold cyan] {translate('project_option_select', lang=lang)}")
        ui.print_message(f" [bold cyan]2.[/bold cyan] {translate('project_option_create', lang=lang)}")
        ui.print_message(f"\n [bold cyan]V.[/bold cyan] {translate('project_option_back', lang=lang)}")
        
        user_choice = ui.ask_string(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "v"]).lower()
        
        if user_choice == "1":
            selected_id_input = ui.ask_string(translate("enter_project_id", lang=lang))
            if selected_id_input.isdigit() and any(proj['id'] == int(selected_id_input) for proj in projects_list):
                db.set_active_project_id(int(selected_id_input))
                break
            else:
                ui.print_message(translate('invalid_option', lang=lang), style="bold red")
                ui.ask_string(translate("press_enter", lang=lang), default="")
        elif user_choice == "2":
            new_project_name = ui.ask_string(translate("project_name_prompt", lang=lang, current="New")).strip()
            if new_project_name:
                try:
                    base_hours_input = int(ui.ask_string(
                        translate("base_hours_prompt", lang=lang, current=config.BASE_HOURS), 
                        default=str(config.BASE_HOURS)
                    ))
                    base_minutes_input = int(ui.ask_string(
                        translate("base_minutes_prompt", lang=lang, current=config.BASE_MINUTES), 
                        default=str(config.BASE_MINUTES)
                    ))
                    new_project_id = db.create_project(new_project_name, base_hours_input, base_minutes_input)
                    db.set_active_project_id(new_project_id)
                    break
                except ValueError:
                    ui.print_message(translate('error_integers', lang=lang), style="bold red")
                    ui.ask_string(translate("press_enter", lang=lang), default="")
        elif user_choice == "v":
            break
