from ..ui import interface as ui
from ..utils.i18n import translate, get_system_language
from ..database.manager import db
from ..utils import files
from .. import config

def config_menu(lang: str = "en"):
    """Submenu for project-specific and global configuration."""
    while True:
        active_id = db.get_active_project_id()
        project = db.get_project_by_id(active_id)
        
        ui.clear_screen()
        ui.print_message(f"\n--- {translate('option_3_clean', lang=lang).upper()} ---", style="bold cyan")
        
        # Display current configuration
        ui.print_message(f"\n [dim]{translate('project_label', lang=lang)}:[/dim] [bold]{project['name']}[/bold]")
        ui.print_message(f" [dim]{translate('base_day_label', lang=lang)}:[/dim] [bold]{project['base_hours']}h {project['base_minutes']}m[/bold]")
        ui.print_message(f" [dim]Language:[/dim] [bold]{db.get_setting('language', 'auto')}[/bold]")
        
        ui.print_message(f"\n[bold dim]>> {translate('config_section_project', lang=lang)}[/bold dim]")
        ui.print_message(f" [bold cyan]1.[/bold cyan] {translate('config_option_edit_name', lang=lang)}")
        ui.print_message(f" [bold cyan]2.[/bold cyan] {translate('config_option_edit_base', lang=lang)}")
        ui.print_message(f" [bold cyan]3.[/bold cyan] {translate('config_option_lang', lang=lang)}")
        
        ui.print_message(f"\n[bold dim]>> {translate('config_section_data', lang=lang)}[/bold dim]")
        ui.print_message(f" [bold cyan]4.[/bold cyan] {translate('config_option_import', lang=lang)}")
        ui.print_message(f" [bold cyan]5.[/bold cyan] {translate('config_option_export', lang=lang)}")
        
        ui.print_message(f"\n [bold cyan]V.[/bold cyan] {translate('config_option_back', lang=lang)}")
        
        choice = ui.ask_string(f"\n{translate('choose_option', lang=lang)}", choices=["1", "2", "3", "4", "5", "v"]).lower()
        
        if choice == "1":
            new_name = ui.ask_string(translate("project_name_prompt", lang=lang, current=project['name']), default=project['name']).strip()
            if new_name:
                db.update_project(active_id, new_name, project['base_hours'], project['base_minutes'])
        elif choice == "2":
            try:
                h = int(ui.ask_string(translate("base_hours_prompt", lang=lang, current=project['base_hours']), default=str(project['base_hours'])))
                m = int(ui.ask_string(translate("base_minutes_prompt", lang=lang, current=project['base_minutes']), default=str(project['base_minutes'])))
                db.update_project(active_id, project['name'], h, m)
            except ValueError:
                ui.print_message(translate('error_integers', lang=lang), style="bold red")
                ui.ask_string(translate("press_enter", lang=lang), default="")
        elif choice == "3":
            lang_opt = ui.ask_string(
                translate("language_prompt", lang=lang, current=db.get_setting("language", "auto")),
                choices=["en", "es", "auto"],
                default="auto"
            ).strip().lower()
            db.set_setting("language", lang_opt)
            # Update local lang for immediate feedback
            lang = lang_opt if lang_opt != "auto" else get_system_language()
        elif choice == "4":
            path = ui.ask_string(translate('import_src_prompt', lang=lang)).strip()
            if path:
                mode = ui.ask_string(
                    translate('import_mode_prompt', lang=lang, merge=config.MODE_MERGE, overwrite=config.MODE_OVERWRITE),
                    choices=[config.MODE_MERGE, config.MODE_OVERWRITE],
                    default=config.MODE_MERGE
                )
                try:
                    source_data = files.read_history_file(path)
                    
                    if mode == config.MODE_OVERWRITE:
                        db.clear_project_records(active_id)
                    else:
                        db.reset_project_balance(active_id)
                    
                    count = 0
                    for date_str, info in source_data['records'].items():
                        db.upsert_record(active_id, date_str, info['hours'], info['minutes'], info['difference'])
                        count += 1
                    ui.print_message(translate('import_success', lang=lang, count=count), style="bold green")
                except Exception as err:
                    ui.print_message(translate('import_error', lang=lang, error=err), style="bold red")
                ui.ask_string(translate('press_enter', lang=lang), default="")
        elif choice == "5":
            path = ui.ask_string(translate('export_dest_prompt', lang=lang)).strip()
            if path:
                try:
                    records = db.get_records(active_id)
                    data_to_export = {
                        "metadata": {
                            "project_name": project['name'],
                            "hours_base": project['base_hours'],
                            "minutes_base": project['base_minutes'],
                            "version": "1.0",
                            "language": db.get_setting("language", "auto")
                        },
                        "records": {r['date']: {'hours': r['hours'], 'minutes': r['minutes'], 'difference': r['difference']} for r in records}
                    }
                    dest = files.export_history(data_to_export, path)
                    ui.print_message(translate('export_success', lang=lang, path=dest), style="bold green")
                except Exception as err:
                    ui.print_message(translate('export_error', lang=lang, error=err), style="bold red")
                ui.ask_string(translate('press_enter', lang=lang), default="")
        elif choice == "v":
            break
