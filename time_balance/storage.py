import sqlite3
import pathlib
import os
from typing import List, Dict, Optional, Any
from . import constants

class DatabaseManager:
    """Manages SQLite database operations for projects and time records."""

    def __init__(self, db_path: pathlib.Path):
        self.db_path = db_path
        # Ensure the directory exists (XDG standard)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a standard sqlite3 connection."""
        return sqlite3.connect(self.db_path)

    def _initialize_database(self):
        """Creates the necessary tables if they do not exist."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            
            # Projects table: configuration for different work contexts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    base_hours INTEGER NOT NULL,
                    base_minutes INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Records table: daily time registrations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    hours INTEGER NOT NULL,
                    minutes INTEGER NOT NULL,
                    difference INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                    UNIQUE(project_id, date)
                )
            """)
            
            # Settings table: global application state (active project, language)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            connection.commit()

            # Seed initial data if empty
            cursor.execute("SELECT COUNT(*) FROM projects")
            if cursor.fetchone()[0] == 0:
                self.create_project("General", constants.BASE_HOURS, constants.BASE_MINUTES)
                # Set the first project as active by default
                cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('active_project_id', '1')")
                cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('language', 'auto')")
                connection.commit()

    def create_project(self, name: str, base_hours: int, base_minutes: int) -> int:
        """Creates a new project and returns its ID."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO projects (name, base_hours, base_minutes) VALUES (?, ?, ?)",
                (name, base_hours, base_minutes)
            )
            return cursor.lastrowid

    def update_project(self, project_id: int, name: str, base_hours: int, base_minutes: int):
        """Updates project configuration."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE projects SET name = ?, base_hours = ?, base_minutes = ? WHERE id = ?",
                (name, base_hours, base_minutes, project_id)
            )

    def get_projects(self) -> List[Dict[str, Any]]:
        """Returns a list of all projects."""
        with self._get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single project by ID."""
        with self._get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_active_project_id(self) -> int:
        """Gets the ID of the project currently in use."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'active_project_id'")
            row = cursor.fetchone()
            if row:
                return int(row[0])
            return 1

    def set_active_project_id(self, project_id: int):
        """Updates the active project ID in settings."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('active_project_id', ?)", (str(project_id),))

    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Retrieves a global setting."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_setting(self, key: str, value: str):
        """Saves a global setting."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

    def upsert_record(self, project_id: int, record_date: str, hours: int, minutes: int, difference: int):
        """Inserts or updates a daily time record."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO records (project_id, date, hours, minutes, difference)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, record_date, hours, minutes, difference))

    def get_records(self, project_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns records for a specific project, sorted by date descending."""
        query = "SELECT * FROM records WHERE project_id = ? ORDER BY date DESC"
        parameters = [project_id]
        if limit:
            query += " LIMIT ?"
            parameters.append(limit)
        
        with self._get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(query, tuple(parameters))
            return [dict(row) for row in cursor.fetchall()]

    def get_record_by_date(self, project_id: int, record_date: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific record for a project and date."""
        with self._get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM records WHERE project_id = ? AND date = ?", (project_id, record_date))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_total_balance(self, project_id: int) -> int:
        """Calculates the sum of differences for all records in a project."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT SUM(difference) FROM records WHERE project_id = ?", (project_id,))
            result = cursor.fetchone()[0]
            return result if result is not None else 0

# --- GLOBAL SINGLETON ---
db = DatabaseManager(constants.DATABASE_PATH)

# --- BACKWARD COMPATIBILITY / SHIMS (TO BE REMOVED) ---
def load_data():
    """Shim for compatibility during migration. Returns active project as a dict."""
    project_id = db.get_active_project_id()
    project = db.get_project_by_id(project_id)
    records_list = db.get_records(project_id)
    
    # Convert list of records to dict by date
    records_dict = {r['date']: {'hours': r['hours'], 'minutes': r['minutes'], 'difference': r['difference']} for r in records_list}
    
    return {
        "metadata": {
            "project_name": project['name'],
            "hours_base": project['base_hours'],
            "minutes_base": project['base_minutes'],
            "language": db.get_setting("language", "auto")
        },
        "records": records_dict
    }

def save_data(data, file_path=None):
    """Shim for compatibility. Saves metadata to the active project."""
    if file_path:
        # If a file_path is provided, we might be exporting or using a non-standard flow
        # For now, we ignore it and warn, or implement as needed.
        pass
        
    project_id = db.get_active_project_id()
    metadata = data.get("metadata", {})
    db.update_project(project_id, metadata['project_name'], metadata['hours_base'], metadata['minutes_base'])
    db.set_setting("language", metadata.get("language", "auto"))
