from ..ui import interface as ui
from ..i18n.translator import translate, resolve_language
from ..database.manager import db
from ..utils import files
from .. import config

def _display_config_status(project_data: dict, current_lang_setting: str, lang: str):
    ui.render_header(translate('option_3_clean', lang=lang))
    ui.render_info_line(translate('project_label', lang=lang), project_data['name'])
    ui.render_info_line(translate('base_day_label', lang=lang), f"{project_data['base_hours']}h {project_data['base_minutes']}m")
    ui.render_info_line("Language", current_lang_setting)

def _display_menu_options(lang: str):
    ui.render_section_title(translate('config_section_project', lang=lang))
    ui.print_message(f"  [bold blue]1.[/bold blue] {translate('config_option_edit_name', lang=lang)}")
    ui.print_message(f"  [bold blue]2.[/bold blue] {translate('config_option_edit_base', lang=lang)}")
    ui.print_message(f"  [bold blue]3.[/bold blue] {translate('config_option_lang', lang=lang)}")
    
    ui.render_section_title(translate('config_section_data', lang=lang))
    ui.print_message(f"  [bold blue]4.[/bold blue] {translate('config_option_import', lang=lang)}")
    ui.print_message(f"  [bold blue]5.[/bold blue] {translate('config_option_export', lang=lang)}")
    ui.print_message(f"  [bold blue]6.[/bold blue] Reparar/Recalcular saldos")
    
    ui.render_navigation_help([("V", translate("config_option_back", lang=lang))])

def _handle_edit_project_name(project_id: int, current_name: str, base_hours: int, base_minutes: int, lang: str):
    new_name = ui.ask_string(
        translate("project_name_prompt", lang=lang, current=current_name), 
        default=current_name
    ).strip()
    if new_name:
        db.update_project(project_id, new_name, base_hours, base_minutes)

def _handle_adjust_base_time(project_id: int, project_name: str, current_h: int, current_m: int, lang: str):
    try:
        new_h = int(ui.ask_string(
            translate("base_hours_prompt", lang=lang, current=current_h), 
            default=str(current_h)
        ))
        new_m = int(ui.ask_string(
            translate("base_minutes_prompt", lang=lang, current=current_m), 
            default=str(current_m)
        ))
        db.update_project(project_id, project_name, new_h, new_m)
    except ValueError:
        ui.print_message(translate('error_integers', lang=lang), style="bold red")
        ui.ask_string(translate("press_enter", lang=lang), default="")

def _handle_change_language(lang: str) -> str:
    lang_opt = ui.ask_string(
        translate("language_prompt", lang=lang, current=db.get_setting("language", "auto")),
        choices=["en", "es", "auto"],
        default="auto"
    ).strip().lower()
    db.set_setting("language", lang_opt)
    return resolve_language(lang_opt)

def _handle_import_data(project_id: int, lang: str):
    import_path = ui.ask_string(translate('import_src_prompt', lang=lang)).strip()
    if not import_path:
        return

    import_mode = ui.ask_string(
        translate('import_mode_prompt', lang=lang, merge=config.MODE_MERGE, overwrite=config.MODE_OVERWRITE),
        choices=[config.MODE_MERGE, config.MODE_OVERWRITE],
        default=config.MODE_MERGE
    )
    
    try:
        source_data = files.read_history_file(import_path)
        if import_mode == config.MODE_OVERWRITE:
            db.clear_project_records(project_id)
        else:
            db.reset_project_balance(project_id)
        
        imported_count = db.import_records(project_id, source_data['records'])
        ui.print_message(translate('import_success', lang=lang, count=imported_count), style="bold green")
    except Exception as err:
        ui.print_message(translate('import_error', lang=lang, error=err), style="bold red")
    ui.ask_string(translate('press_enter', lang=lang), default="")

def _handle_export_data(project_id: int, project_data: dict, lang: str):
    export_path = ui.ask_string(translate('export_dest_prompt', lang=lang)).strip()
    if not export_path:
        return

    try:
        data_to_export = {
            "metadata": {
                "project_name": project_data['name'],
                "hours_base": project_data['base_hours'],
                "minutes_base": project_data['base_minutes'],
                "version": "1.0",
                "language": db.get_setting("language", "auto")
            },
            "records": db.get_records_dict(project_id)
        }
        dest = files.export_history(data_to_export, export_path)
        ui.print_message(translate('export_success', lang=lang, path=dest), style="bold green")
    except Exception as err:
        ui.print_message(translate('export_error', lang=lang, error=err), style="bold red")
    ui.ask_string(translate('press_enter', lang=lang), default="")


def _handle_recalculate_balances(lang: str):
    """Forces a recalculation of all balances."""
    if ui.ask_confirm("¿Recalcular TODOS los saldos desde el historial?"):
        db.recalculate_all_balances()
        ui.print_message("\n✅ Saldos recalculados correctamente.", style="bold green")
    ui.ask_string(translate('press_enter', lang=lang), default="")


def config_menu(lang: str = "en"):
    """Submenu for project-specific and global configuration."""
    while True:
        active_id = db.get_active_project_id()
        project = db.get_project_by_id(active_id)
        lang_setting = db.get_setting("language", "auto")
        
        ui.clear_screen()
        _display_config_status(project, lang_setting, lang)
        _display_menu_options(lang)
        
        choice = ui.ask_string(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "3", "4", "5", "6", "v"]).lower()
        
        if choice == "1":
            _handle_edit_project_name(active_id, project['name'], project['base_hours'], project['base_minutes'], lang)
        elif choice == "2":
            _handle_adjust_base_time(active_id, project['name'], project['base_hours'], project['base_minutes'], lang)
        elif choice == "3":
            lang = _handle_change_language(lang)
        elif choice == "4":
            _handle_import_data(active_id, lang)
        elif choice == "5":
            _handle_export_data(active_id, project, lang)
        elif choice == "6":
            _handle_recalculate_balances(lang)
        elif choice == "v":
            break
