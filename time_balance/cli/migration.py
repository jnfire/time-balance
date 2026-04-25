from datetime import date
from ..ui import interface as ui
from ..i18n.translator import translate
from ..database.manager import db
from ..utils import files
from .. import config

def migrate_from_json(path: str, lang: str):
    """Migrates records from a legacy JSON file to the SQLite database."""
    try:
        source_data = files.read_history_file(path)
        metadata = source_data.get("metadata", {})
        
        ui.print_message(f"\n{translate('import_header', lang=lang, date=path)}", style="bold cyan")
        
        # 1. Create the project
        project_name = metadata.get("project_name", f"Imported {date.today()}")
        base_h = metadata.get("hours_base", config.BASE_HOURS)
        base_m = metadata.get("minutes_base", config.BASE_MINUTES)
        
        new_project_id = db.create_project(project_name, base_h, base_m)
        db.set_active_project_id(new_project_id)
        
        # 2. Bulk insert records using centralized method
        records_to_import = source_data.get("records", {})
        imported_count = db.import_records(new_project_id, records_to_import)
            
        ui.print_message(translate('import_success', lang=lang, count=imported_count), style="bold green")
        ui.print_message(f"   {translate('project_label', lang=lang)}: [bold]{project_name}[/bold] (ID: {new_project_id})")
        
    except Exception as error:
        ui.print_message(translate('import_error', lang=lang, error=error), style="bold red")
