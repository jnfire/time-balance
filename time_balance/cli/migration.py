from datetime import date
from ..ui import interface as ui
from ..utils.i18n import translate
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
        h = metadata.get("hours_base", config.BASE_HOURS)
        m = metadata.get("minutes_base", config.BASE_MINUTES)
        
        new_id = db.create_project(project_name, h, m)
        db.set_active_project_id(new_id)
        
        # 2. Insert records
        count = 0
        records = source_data.get("records", {})
        for date_str, info in records.items():
            db.upsert_record(new_id, date_str, info['hours'], info['minutes'], info['difference'])
            count += 1
            
        ui.print_message(translate('import_success', lang=lang, count=count), style="bold green")
        ui.print_message(f"   {translate('project_label', lang=lang)}: [bold]{project_name}[/bold] (ID: {new_id})")
        
    except Exception as err:
        ui.print_message(translate('import_error', lang=lang, error=err), style="bold red")
