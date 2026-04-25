from ..ui import interface as ui
from ..utils.i18n import translate, get_system_language
from ..database.manager import db
from ..utils import files
from .. import config

def config_menu(lang: str = "en"):
    """Submenu for project-specific and global configuration."""
    while True:
        active_project_id = db.get_active_project_id()
        current_project = db.get_project_by_id(active_project_id)
        
        ui.clear_screen()
        ui.print_message(f"\n--- {translate('option_3_clean', lang=lang).upper()} ---", style="bold cyan")
        
        # Display current configuration
        ui.print_message(f"\n [dim]{translate('project_label', lang=lang)}:[/dim] [bold]{current_project['name']}[/bold]")
        ui.print_message(f" [dim]{translate('base_day_label', lang=lang)}:[/dim] [bold]{current_project['base_hours']}h {current_project['base_minutes']}m[/bold]")
        ui.print_message(f" [dim]Language:[/dim] [bold]{db.get_setting('language', 'auto')}[/bold]")
        
        ui.print_message(f"\n[bold dim]>> {translate('config_section_project', lang=lang)}[/bold dim]")
        ui.print_message(f" [bold cyan]1.[/bold cyan] {translate('config_option_edit_name', lang=lang)}")
        ui.print_message(f" [bold cyan]2.[/bold cyan] {translate('config_option_edit_base', lang=lang)}")
        ui.print_message(f" [bold cyan]3.[/bold cyan] {translate('config_option_lang', lang=lang)}")
        
        ui.print_message(f"\n[bold dim]>> {translate('config_section_data', lang=lang)}[/bold dim]")
        ui.print_message(f" [bold cyan]4.[/bold cyan] {translate('config_option_import', lang=lang)}")
        ui.print_message(f" [bold cyan]5.[/bold cyan] {translate('config_option_export', lang=lang)}")
        
        ui.print_message(f"\n [bold cyan]V.[/bold cyan] {translate('config_option_back', lang=lang)}")
        
        menu_choice = ui.ask_string(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "3", "4", "5", "v"]).lower()
        
        if menu_choice == "1":
            new_project_name = ui.ask_string(
                translate("project_name_prompt", lang=lang, current=current_project['name']), 
                default=current_project['name']
            ).strip()
            if new_project_name:
                db.update_project(active_project_id, new_project_name, current_project['base_hours'], current_project['base_minutes'])
        elif menu_choice == "2":
            try:
                new_base_hours = int(ui.ask_string(
                    translate("base_hours_prompt", lang=lang, current=current_project['base_hours']), 
                    default=str(current_project['base_hours'])
                ))
                new_base_minutes = int(ui.ask_string(
                    translate("base_minutes_prompt", lang=lang, current=current_project['base_minutes']), 
                    default=str(current_project['base_minutes'])
                ))
                db.update_project(active_project_id, current_project['name'], new_base_hours, new_base_minutes)
            except ValueError:
                ui.print_message(translate('error_integers', lang=lang), style="bold red")
                ui.ask_string(translate("press_enter", lang=lang), default="")
        elif menu_choice == "3":
            selected_language = ui.ask_string(
                translate("language_prompt", lang=lang, current=db.get_setting("language", "auto")),
                choices=["en", "es", "auto"],
                default="auto"
            ).strip().lower()
            db.set_setting("language", selected_language)
            # Update local lang for immediate feedback
            lang = selected_language if selected_language != "auto" else get_system_language()
        elif menu_choice == "4":
            import_path = ui.ask_string(translate('import_src_prompt', lang=lang)).strip()
            if import_path:
                import_mode = ui.ask_string(
                    translate('import_mode_prompt', lang=lang, merge=config.MODE_MERGE, overwrite=config.MODE_OVERWRITE),
                    choices=[config.MODE_MERGE, config.MODE_OVERWRITE],
                    default=config.MODE_MERGE
                )
                try:
                    source_history_data = files.read_history_file(import_path)
                    
                    if import_mode == config.MODE_OVERWRITE:
                        db.clear_project_records(active_project_id)
                    else:
                        db.reset_project_balance(active_project_id)
                    
                    imported_records_count = 0
                    for record_date, record_info in source_history_data['records'].items():
                        db.upsert_record(
                            active_project_id, 
                            record_date, 
                            record_info['hours'], 
                            record_info['minutes'], 
                            record_info['difference']
                        )
                        imported_records_count += 1
                    ui.print_message(translate('import_success', lang=lang, count=imported_records_count), style="bold green")
                except Exception as error_msg:
                    ui.print_message(translate('import_error', lang=lang, error=error_msg), style="bold red")
                ui.ask_string(translate("press_enter", lang=lang), default="")
        elif menu_choice == "5":
            export_path = ui.ask_string(translate('export_dest_prompt', lang=lang)).strip()
            if export_path:
                try:
                    all_project_records = db.get_records(active_project_id)
                    data_to_export = {
                        "metadata": {
                            "project_name": current_project['name'],
                            "hours_base": current_project['base_hours'],
                            "minutes_base": current_project['base_minutes'],
                            "version": "1.0",
                            "language": db.get_setting("language", "auto")
                        },
                        "records": {
                            record['date']: {
                                'hours': record['hours'], 
                                'minutes': record['minutes'], 
                                'difference': record['difference']
                            } for record in all_project_records
                        }
                    }
                    final_destination = files.export_history(data_to_export, export_path)
                    ui.print_message(translate('export_success', lang=lang, path=final_destination), style="bold green")
                except Exception as error_msg:
                    ui.print_message(translate('export_error', lang=lang, error=error_msg), style="bold red")
                ui.ask_string(translate("press_enter", lang=lang), default="")
        elif menu_choice == "v":
            break
