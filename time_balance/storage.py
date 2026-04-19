import os
import json
import tempfile
import shutil
import errno
from datetime import datetime
from . import constants


def _resolve_file_path(file_path=None):
    """Resolves the final history file path."""
    if file_path:
        path = file_path
    elif constants.ENV_HISTORIAL in os.environ and os.environ[constants.ENV_HISTORIAL].strip():
        path = os.environ[constants.ENV_HISTORIAL]
    else:
        path = constants.ARCHIVO_DATOS

    path = os.path.expanduser(path)
    return os.path.abspath(path)


def load_data(file_path=None):
    """Loads history from the structured JSON file."""
    path = _resolve_file_path(file_path)
    
    # Return empty skeleton if file doesn't exist
    if not os.path.exists(path):
        return {
            "metadata": {
                "project_name": "General",
                "hours_base": constants.HORAS_BASE,
                "minutes_base": constants.MINUTOS_BASE,
                "version": "1.0",
                "language": "auto"
            },
            "records": {}
        }
        
    try:
        with open(path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except (ValueError, json.JSONDecodeError):
        # On error, we return an empty structure
        return load_data(file_path="/dev/null") # Simple way to get skeleton


def save_data(data, file_path=None):
    """Saves complete history using atomic writing."""
    path = _resolve_file_path(file_path)
    dest_dir = os.path.dirname(path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    content = json.dumps(data, indent=4, ensure_ascii=False)
    file_descriptor, temp_path = tempfile.mkstemp(prefix="history_", suffix=".json", dir=dest_dir or ".")
    try:
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as temp_file:
            temp_file.write(content)
            try:
                temp_file.flush()
                os.fsync(temp_file.fileno())
            except Exception:
                pass

        try:
            os.replace(temp_path, path)
        except OSError as error:
            if getattr(error, 'errno', None) == errno.EXDEV:
                shutil.copy2(temp_path, path)
                os.remove(temp_path)
            else:
                raise
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def _create_backup(file_path):
    """Creates a timestamped backup of the given file."""
    if not os.path.exists(file_path):
        return None
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    backup = f"{file_path}.bak.{timestamp}"
    shutil.copy2(file_path, backup)
    try:
        shutil.copy2(file_path, f"{file_path}.bak")
    except Exception:
        pass
    return backup
