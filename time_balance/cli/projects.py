from ..ui import interface as ui
from ..i18n.translator import translate
from ..database.manager import db
from .. import config

def project_menu(lang: str = "en"):
    """Submenu for switching and creating projects directly."""
    while True:
        projects_list = db.get_projects()
        active_project_id = db.get_active_project_id()

        ui.clear_screen()
        ui.render_header(translate('option_4_clean', lang=lang))
        
        table_columns = [
            ("ID", {"justify": "center", "style": "dim"}),
            ("Name", {"style": "bold"}),
            ("Base", {"justify": "center", "style": "dim"}),
            ("Active", {"justify": "center"})
        ]
        
        table_rows = []
        for project in projects_list:
            is_active_marker = "[bold blue]●[/bold blue]" if project['id'] == active_project_id else ""
            table_rows.append([
                str(project['id']), 
                project['name'], 
                f"{project['base_hours']}h {project['base_minutes']}m", 
                is_active_marker
            ])
        
        ui.render_simple_table(table_columns, table_rows)
            
        # Unified navigation help
        ui.render_navigation_help([
            ("ID", translate("project_option_select", lang=lang)),
            ("C", translate("project_option_create", lang=lang)),
            ("V", translate("project_option_back", lang=lang))
        ])
        
        # We accept IDs (numbers) or navigation keys
        valid_ids = [str(project['id']) for project in projects_list]
        choice_options = valid_ids + ["c", "v"]
        
        user_choice = ui.ask_string(f"\n{translate('choose_option', lang=lang)}", choices=choice_options).lower()
        
        if user_choice.isdigit():
            selected_id = int(user_choice)
            if any(project['id'] == selected_id for project in projects_list):
                db.set_active_project_id(selected_id)
                break
        elif user_choice == "c":
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
