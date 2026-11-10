import os
import pathlib
import sys


# --- VERSION ---
def _get_version():
    try:
        version_path = pathlib.Path(__file__).parent / "VERSION"
        return version_path.read_text().strip()
    except Exception:
        return "0.0.0-unknown"


VERSION = _get_version()


# --- PATH CONFIGURATION ---
def get_data_dir() -> pathlib.Path:
    """The standard per-user folder for the application data."""
    home = pathlib.Path.home()
    if os.name == "nt":
        base = pathlib.Path(os.getenv("APPDATA") or home / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    else:
        base = pathlib.Path(os.getenv("XDG_DATA_HOME") or home / ".local" / "share")
    return base / "time-balance"


DATA_DIR = get_data_dir()
DATABASE_PATH = DATA_DIR / "time_balance.db"

# --- TIME CONFIGURATION ---
BASE_HOURS = 7
BASE_MINUTES = 45

# --- IMPORT MODES ---
MODE_MERGE = "merge"
MODE_OVERWRITE = "overwrite"

VALID_IMPORT_MODES = [MODE_MERGE, MODE_OVERWRITE]
