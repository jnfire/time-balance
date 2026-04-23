import os
import pathlib

VERSION = "0.3.0"

# --- PATH CONFIGURATION ---
def get_data_dir() -> pathlib.Path:
    """Get the standard directory for storing application data."""
    if os.name == 'nt':
        # Windows
        base_dir = os.getenv('APPDATA')
        if not base_dir:
            base_dir = pathlib.Path.home() / "AppData" / "Roaming"
        else:
            base_dir = pathlib.Path(base_dir)
    elif os.uname().sysname == 'Darwin':
        # macOS
        base_dir = pathlib.Path.home() / "Library" / "Application Support"
    else:
        # Linux / Other
        base_dir = os.getenv('XDG_DATA_HOME')
        if not base_dir:
            base_dir = pathlib.Path.home() / ".local" / "share"
        else:
            base_dir = pathlib.Path(base_dir)
    
    data_dir = pathlib.Path(base_dir) / "time-balance"
    return data_dir

DATA_DIR = get_data_dir()
DATABASE_PATH = DATA_DIR / "time_balance.db"

# --- TIME CONFIGURATION ---
BASE_HOURS = 7
BASE_MINUTES = 45

# --- PERSISTENCE (LEGACY/ENV) ---
ENV_HISTORIAL = "HISTORIAL_PATH"

# --- IMPORT MODES ---
MODE_MERGE = "merge"
MODE_OVERWRITE = "overwrite"

VALID_IMPORT_MODES = [MODE_MERGE, MODE_OVERWRITE]
