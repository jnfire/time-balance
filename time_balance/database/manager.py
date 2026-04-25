import sqlite3
import pathlib
import os
import contextlib
from typing import List, Dict, Optional, Any
from .. import config

class DatabaseManager:
    """Manages SQLite database operations for projects and time records."""

    def __init__(self, db_path: pathlib.Path):
        self.db_path = db_path
        # Ensure the directory exists (XDG standard)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    @contextlib.contextmanager
    def _get_connection(self):
        """Context manager that yields a database connection, handling transactions and closing."""
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            # The connection object itself is a context manager for transactions
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize_database(self):
        """Creates the necessary tables if they do not exist and handles migrations."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            
            # Projects table: configuration for different work contexts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    base_hours INTEGER NOT NULL,
                    base_minutes INTEGER NOT NULL,
                    total_balance INTEGER DEFAULT NULL,
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

            # Seed initial data if empty
            cursor.execute("SELECT COUNT(*) FROM projects")
            projects_count = cursor.fetchone()[0]
            if projects_count == 0:
                cursor.execute(
                    "INSERT INTO projects (name, base_hours, base_minutes) VALUES (?, ?, ?)",
                    ("General", config.BASE_HOURS, config.BASE_MINUTES)
                )
                # Set the first project as active by default
                cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('active_project_id', '1')")
                cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('language', 'auto')")

    def _get_record_difference(self, cursor: sqlite3.Cursor, project_id: int, record_date: str) -> int:
        """Helper to get the difference value of an existing record."""
        cursor.execute("SELECT difference FROM records WHERE project_id = ? AND date = ?", (project_id, record_date))
        record_row = cursor.fetchone()
        return record_row[0] if record_row else 0

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
            return [dict(project_row) for project_row in cursor.fetchall()]

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single project by ID."""
        with self._get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            project_row = cursor.fetchone()
            return dict(project_row) if project_row else None

    def get_active_project_id(self) -> int:
        """Gets the ID of the project currently in use."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'active_project_id'")
            setting_row = cursor.fetchone()
            if setting_row:
                return int(setting_row[0])
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
            setting_row = cursor.fetchone()
            return setting_row[0] if setting_row else default

    def set_setting(self, key: str, value: str):
        """Saves a global setting."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

    def upsert_record(self, project_id: int, record_date: str, hours: int, minutes: int, difference: int):
        """Inserts or updates a daily time record and updates project total balance cache."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            
            # 1. Get old difference to adjust balance
            old_difference = self._get_record_difference(cursor, project_id, record_date)
            
            # 2. Upsert the record
            cursor.execute("""
                INSERT OR REPLACE INTO records (project_id, date, hours, minutes, difference)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, record_date, hours, minutes, difference))
            
            # 3. Update project total balance cache
            cursor.execute("""
                UPDATE projects 
                SET total_balance = total_balance - ? + ? 
                WHERE id = ? AND total_balance IS NOT NULL
            """, (old_difference, difference, project_id))

    def delete_record(self, project_id: int, record_date: str):
        """Deletes a record and updates project total balance cache."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            
            # 1. Get difference to subtract from total
            cursor.execute("SELECT difference FROM records WHERE project_id = ? AND date = ?", (project_id, record_date))
            record_row = cursor.fetchone()
            if not record_row:
                return

            current_difference = record_row[0]
            
            # 2. Delete the record
            cursor.execute("DELETE FROM records WHERE project_id = ? AND date = ?", (project_id, record_date))
            
            # 3. Update project total balance cache
            cursor.execute("""
                UPDATE projects 
                SET total_balance = total_balance - ? 
                WHERE id = ? AND total_balance IS NOT NULL
            """, (current_difference, project_id))

    def clear_project_records(self, project_id: int):
        """Removes all records for a project and resets its balance cache."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM records WHERE project_id = ?", (project_id,))
            cursor.execute("UPDATE projects SET total_balance = 0 WHERE id = ?", (project_id,))

    def delete_project(self, project_id: int):
        """Deletes a project and all its records."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            # Records are deleted automatically due to ON DELETE CASCADE if supported,
            # but we do it explicitly to be safe and clear.
            cursor.execute("DELETE FROM records WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))

    def recalculate_all_balances(self):
        """Forces a full recalculation for all projects in the database."""
        projects = self.get_projects()
        for project in projects:
            self.recalculate_project_balance(project['id'])

    def get_records(self, project_id: int, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Returns records for a specific project, sorted by date descending with pagination support."""
        query = "SELECT * FROM records WHERE project_id = ? ORDER BY date DESC"
        parameters = [project_id]
        
        if limit:
            query += " LIMIT ?"
            parameters.append(limit)
            if offset > 0:
                query += " OFFSET ?"
                parameters.append(offset)
        
        with self._get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(query, tuple(parameters))
            return [dict(record_row) for record_row in cursor.fetchall()]

    def get_record_by_date(self, project_id: int, record_date: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific record for a project and date."""
        with self._get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM records WHERE project_id = ? AND date = ?", (project_id, record_date))
            record_row = cursor.fetchone()
            return dict(record_row) if record_row else None

    def get_total_balance(self, project_id: int) -> int:
        """Retrieves the cached balance or calculates it if NULL."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            
            # Try to get cached balance
            cursor.execute("SELECT total_balance FROM projects WHERE id = ?", (project_id,))
            project_row = cursor.fetchone()
            
            if project_row and project_row[0] is not None:
                return project_row[0]
        
        # Recalculate if NULL
        return self.recalculate_project_balance(project_id)

    def recalculate_project_balance(self, project_id: int) -> int:
        """Forces a full recalculation of the balance from all records and updates the cache."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT SUM(difference) FROM records WHERE project_id = ?", (project_id,))
            sum_result = cursor.fetchone()[0]
            total_sum = sum_result if sum_result is not None else 0
            
            cursor.execute("UPDATE projects SET total_balance = ? WHERE id = ?", (total_sum, project_id))
            return total_sum

    def reset_project_balance(self, project_id: int):
        """Resets the project balance cache to NULL, forcing a recalculation on next access."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE projects SET total_balance = NULL WHERE id = ?", (project_id,))

    def count_records(self, project_id: int) -> int:
        """Returns the total number of records for a specific project."""
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM records WHERE project_id = ?", (project_id,))
            return cursor.fetchone()[0]

    def import_records(self, project_id: int, records_dict: Dict[str, dict]) -> int:
        """Imports a dictionary of records into the database. Returns count of imported items."""
        imported_count = 0
        for record_date, record_info in records_dict.items():
            self.upsert_record(
                project_id, 
                record_date, 
                record_info['hours'], 
                record_info['minutes'], 
                record_info['difference']
            )
            imported_count += 1
        return imported_count

    def get_records_dict(self, project_id: int) -> Dict[str, dict]:
        """Returns all records for a project as a dictionary formatted for JSON export."""
        all_records = self.get_records(project_id)
        return {
            record['date']: {
                'hours': record['hours'], 
                'minutes': record['minutes'], 
                'difference': record['difference']
            } for record in all_records
        }

# --- GLOBAL SINGLETON ---
db = DatabaseManager(config.DATABASE_PATH)
