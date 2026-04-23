import locale

# --- TRANSLATIONS ---

STRINGS = {
    "en": {
        "menu_title": "CONTROL CENTER",
        "project_label": "PROJECT",
        "balance_label": "TOTAL ACCUMULATED BALANCE",
        "base_day_label": "Daily base",
        "option_1": "1. Register workday (or correct day)",
        "option_2": "2. View recent records",
        "option_3": "3. Manage projects (switch/create/edit)",
        "option_4": "4. Export history to file",
        "option_5": "5. Import history from file",
        "option_6": "6. Exit",
        "option_7": "7. (Reserved)",
        "projects_menu_header": "PROJECT MANAGEMENT",
        "switch_project": "1. Switch project",
        "create_project": "2. Create new project",
        "edit_project": "3. Edit current project configuration",
        "back": "4. Back to main menu",
        "enter_project_id": "Enter project ID to switch: ",
        "invalid_option": "❌ Invalid option.",
        "migration_success": "\n✅ Successfully migrated {count} records to project '{name}'.",
        "migration_error": "❌ Migration error: {error}",
        "choose_option": "Choose option: ",
        "press_enter": "\nPress ENTER to continue...",
        "exit_msg": "See you tomorrow!",
        "date_prompt": "\nRecord date (Enter for TODAY: {today})",
        "date_input": "Or enter date (YYYY-MM-DD): ",
        "invalid_date": "❌ Invalid date format. Using today's date.",
        "duplicate_warning": "\n⚠️  WARNING: A record already exists for {date}.",
        "previous_record": "   Previously recorded: {hours}h {minutes}m",
        "overwrite_confirm": "Do you want to OVERWRITE it? (y/n): ",
        "op_cancelled": "Operation cancelled.",
        "input_header": "--- Entering data for: {date} ---",
        "hours_worked": "Hours worked: ",
        "minutes_worked": "Minutes worked: ",
        "error_integers": "❌ Error: Please enter integer numbers.",
        "save_success": "\n✅ Record saved for {date}.",
        "day_diff": "   Day difference: {diff}",
        "recent_records_header": "\n--- Last {limit} records ---",
        "full_history_header": "\n--- Full history ---",
        "no_records": "No records found.",
        "config_header": "\n--- Project Configuration ---",
        "project_name_prompt": "Project name [{current}]: ",
        "base_hours_prompt": "Daily base hours [{current}]: ",
        "base_minutes_prompt": "Daily base minutes [{current}]: ",
        "language_prompt": "System language (en/es/auto) [{current}]: ",
        "invalid_language": "❌ Invalid language. Please use 'en', 'es', or 'auto'.",
        "export_dest_prompt": "Destination path (e.g.: /path/my_export.json): ",
        "export_success": "\n✅ Exported to: {path}",
        "export_error": "Error exporting: {error}",
        "import_src_prompt": "Source path to import: ",
        "import_mode_prompt": "Mode ({merge}/{overwrite}) [{merge}]: ",
        "import_success": "\n✅ Import completed. Total entries now: {count}",
        "import_error": "Error importing: {error}",
        "status_project": "Project: {name}",
        "status_balance": "Accumulated balance: {balance}",
        "work_label": "Work",
        "balance_short_label": "Bal"
    },
    "es": {
        "menu_title": "CENTRO DE CONTROL",
        "project_label": "PROYECTO",
        "balance_label": "SALDO TOTAL ACUMULADO",
        "base_day_label": "Base diaria",
        "option_1": "1. Registrar jornada (o corregir día)",
        "option_2": "2. Ver últimos registros",
        "option_3": "3. Gestionar proyectos (cambiar/crear/editar)",
        "option_4": "4. Exportar historial a archivo",
        "option_5": "5. Importar historial desde archivo",
        "option_6": "6. Salir",
        "option_7": "7. (Reservado)",
        "projects_menu_header": "GESTIÓN DE PROYECTOS",
        "switch_project": "1. Cambiar de proyecto",
        "create_project": "2. Crear nuevo proyecto",
        "edit_project": "3. Editar configuración del proyecto actual",
        "back": "4. Volver al menú principal",
        "enter_project_id": "Introduce el ID del proyecto para cambiar: ",
        "invalid_option": "❌ Opción inválida.",
        "migration_success": "\n✅ Migrados con éxito {count} registros al proyecto '{name}'.",
        "migration_error": "❌ Error de migración: {error}",
        "choose_option": "Elige opción: ",
        "press_enter": "\nPresiona ENTER para continuar...",
        "exit_msg": "¡Hasta mañana!",
        "date_prompt": "\nFecha del registro (Enter para usar HOY: {today})",
        "date_input": "O introduce fecha (YYYY-MM-DD): ",
        "invalid_date": "❌ Formato de fecha incorrecto. Usando fecha de hoy.",
        "duplicate_warning": "\n⚠️  ATENCIÓN: Ya existe un registro para el día {date}.",
        "previous_record": "   Registrado anteriormente: {hours}h {minutes}m",
        "overwrite_confirm": "¿Quieres SOBREESCRIBIRLO? (s/n): ",
        "op_cancelled": "Operación cancelada.",
        "input_header": "--- Introduciendo datos para: {date} ---",
        "hours_worked": "Horas trabajadas: ",
        "minutes_worked": "Minutos trabajados: ",
        "error_integers": "❌ Error: Introduce números enteros.",
        "save_success": "\n✅ Registro guardado para el {date}.",
        "day_diff": "   Diferencia del día: {diff}",
        "recent_records_header": "\n--- Últimos {limit} registros ---",
        "full_history_header": "\n--- Historial completo ---",
        "no_records": "No hay registros.",
        "config_header": "\n--- Configuración del Proyecto ---",
        "project_name_prompt": "Nombre del proyecto [{current}]: ",
        "base_hours_prompt": "Horas base diaria [{current}]: ",
        "base_minutes_prompt": "Minutos base diaria [{current}]: ",
        "language_prompt": "Idioma del sistema (en/es/auto) [{current}]: ",
        "invalid_language": "❌ Idioma inválido. Por favor, usa 'en', 'es' o 'auto'.",
        "export_dest_prompt": "Ruta destino (ej: /ruta/mi_export.json): ",
        "export_success": "\n✅ Exportado en: {path}",
        "export_error": "Error al exportar: {error}",
        "import_src_prompt": "Ruta fuente a importar: ",
        "import_mode_prompt": "Modo ({merge}/{overwrite}) [{merge}]: ",
        "import_success": "\n✅ Importación completada. Entradas totales ahora: {count}",
        "import_error": "Error al importar: {error}",
        "status_project": "Proyecto: {name}",
        "status_balance": "Saldo acumulado: {balance}",
        "work_label": "Trabajo",
        "balance_short_label": "Bal"
    }
}

def get_system_language():
    """Detects system language using modern locale API, defaults to English."""
    try:
        # Preferred modern way to get language code
        lang_code, _ = locale.getlocale()
        if not lang_code:
             # Fallback to preferred encoding logic or environment
            lang_code = locale.getdefaultlocale()[0]
            
        if lang_code and lang_code.startswith("es"):
            return "es"
    except Exception:
        pass
    return "en"

def translate(key, lang="en", **kwargs):
    """Returns the translated string for a given key."""
    language_dict = STRINGS.get(lang, STRINGS["en"])
    template = language_dict.get(key, STRINGS["en"].get(key, key))
    return template.format(**kwargs)
