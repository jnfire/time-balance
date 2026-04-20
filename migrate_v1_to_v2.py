import json
import os
import sys
from datetime import datetime

def migrate(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON: {e}")
            return

    # Check if migration is needed
    if isinstance(data, dict) and "records" in data and "metadata" in data:
        print("File is already in the new format (v2). No migration needed.")
        return

    print(f"Migrating {file_path} to v2 format...")

    # Determine structure (flat legacy vs structured es)
    is_structured_es = isinstance(data, dict) and "registros" in data
    raw_records = data["registros"] if is_structured_es else data
    metadata = data.get("metadata", {}) if is_structured_es else {}

    # 1. Migrate records
    new_records = {}
    if isinstance(raw_records, dict):
        for date_key, info in raw_records.items():
            if isinstance(info, dict):
                new_records[date_key] = {
                    "hours": info.get("hours", info.get("horas", 0)),
                    "minutes": info.get("minutes", info.get("minutos", 0)),
                    "difference": info.get("difference", info.get("diferencia", 0))
                }

    # 2. Migrate metadata
    new_metadata = {
        "project_name": metadata.get("project_name", "General"),
        "hours_base": metadata.get("hours_base", metadata.get("horas_base", 7)),
        "minutes_base": metadata.get("minutes_base", metadata.get("minutos_base", 45)),
        "version": "1.0",
        "language": metadata.get("language", "auto")
    }

    new_data = {
        "metadata": new_metadata,
        "records": new_records
    }

    # 3. Save backup and overwrite
    backup_path = f"{file_path}.pre_migration.bak"
    os.rename(file_path, backup_path)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Migration successful!")
    print(f"   Original file backed up at: {backup_path}")
    print(f"   New format saved at: {file_path}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "historial_hours.json"
    migrate(path)
