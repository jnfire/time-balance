"""SQLite persistence for projects, daily records and settings."""

from __future__ import annotations

import contextlib
import pathlib
import sqlite3
from collections.abc import Iterator, Sequence
from typing import Any, cast

from .. import config
from .models import Project, Record, RecordData

SETTING_ACTIVE_PROJECT = "active_project_id"
SETTING_LANGUAGE = "language"
DEFAULT_PROJECT_NAME = "General"

_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        base_hours INTEGER NOT NULL,
        base_minutes INTEGER NOT NULL,
        total_balance INTEGER DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """,
)


class DatabaseManager:
    """Reads and writes the application data.

    The balance of each project is cached in ``projects.total_balance``. A write
    that changes a record adjusts the cache in the same transaction. A NULL cache
    means "unknown" and is rebuilt from the records the next time it is read.
    """

    def __init__(self, db_path: pathlib.Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    # --- Connection and query helpers ---

    @contextlib.contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Yields a connection that commits on success, rolls back on error and always closes."""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _fetch_all(self, sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        with self._get_connection() as connection:
            return [dict(row) for row in connection.execute(sql, params).fetchall()]

    def _fetch_one(self, sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        with self._get_connection() as connection:
            row = connection.execute(sql, params).fetchone()
            return dict(row) if row else None

    def _fetch_value(self, sql: str, params: Sequence[Any] = ()) -> Any:
        """Returns the first column of the first row, or None when there is no row."""
        with self._get_connection() as connection:
            row = connection.execute(sql, params).fetchone()
            return row[0] if row else None

    def _initialize_database(self) -> None:
        """Creates the tables and, on the first run, the default project."""
        with self._get_connection() as connection:
            for statement in _SCHEMA:
                connection.execute(statement)
            if connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
                cursor = connection.execute(
                    "INSERT INTO projects (name, base_hours, base_minutes) VALUES (?, ?, ?)",
                    (DEFAULT_PROJECT_NAME, config.BASE_HOURS, config.BASE_MINUTES),
                )
                connection.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (SETTING_ACTIVE_PROJECT, str(cursor.lastrowid)),
                )
                connection.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, 'auto')",
                    (SETTING_LANGUAGE,),
                )

    # --- Projects ---

    def create_project(self, name: str, base_hours: int, base_minutes: int) -> int:
        """Creates a project and returns its id."""
        with self._get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO projects (name, base_hours, base_minutes) VALUES (?, ?, ?)",
                (name, base_hours, base_minutes),
            )
            return cast(int, cursor.lastrowid)

    def update_project(
        self, project_id: int, name: str, base_hours: int, base_minutes: int
    ) -> None:
        with self._get_connection() as connection:
            connection.execute(
                "UPDATE projects SET name = ?, base_hours = ?, base_minutes = ? WHERE id = ?",
                (name, base_hours, base_minutes, project_id),
            )

    def get_projects(self) -> list[Project]:
        """All projects, ordered by name."""
        return cast("list[Project]", self._fetch_all("SELECT * FROM projects ORDER BY name"))

    def get_project_by_id(self, project_id: int) -> Project | None:
        row = self._fetch_one("SELECT * FROM projects WHERE id = ?", (project_id,))
        return cast("Project | None", row)

    def delete_project(self, project_id: int) -> None:
        """Deletes a project. Its records go with it (``ON DELETE CASCADE``)."""
        with self._get_connection() as connection:
            connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))

    # --- Active project and settings ---

    def get_active_project_id(self) -> int:
        """Id of the project in use, or 1 if none has been chosen yet."""
        stored_id = self.get_setting(SETTING_ACTIVE_PROJECT, "")
        return int(stored_id) if stored_id else 1

    def set_active_project_id(self, project_id: int) -> None:
        self.set_setting(SETTING_ACTIVE_PROJECT, str(project_id))

    def get_active_project(self) -> Project:
        """The project in use.

        If the stored id no longer exists (for example the project was deleted
        from another process), the first project becomes the active one.
        """
        project = self.get_project_by_id(self.get_active_project_id())
        if project is not None:
            return project
        fallback = self.get_projects()[0]
        self.set_active_project_id(fallback["id"])
        return fallback

    def get_setting(self, key: str, default: str) -> str:
        value = self._fetch_value("SELECT value FROM settings WHERE key = ?", (key,))
        return default if value is None else str(value)

    def set_setting(self, key: str, value: str) -> None:
        with self._get_connection() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
            )

    # --- Records ---

    def upsert_record(
        self, project_id: int, record_date: str, hours: int, minutes: int, difference: int
    ) -> None:
        """Inserts or replaces a day and adjusts the cached balance in the same transaction."""
        with self._get_connection() as connection:
            previous = connection.execute(
                "SELECT difference FROM records WHERE project_id = ? AND date = ?",
                (project_id, record_date),
            ).fetchone()
            previous_difference = previous[0] if previous else 0
            connection.execute(
                """
                INSERT OR REPLACE INTO records (project_id, date, hours, minutes, difference)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, record_date, hours, minutes, difference),
            )
            connection.execute(
                "UPDATE projects SET total_balance = COALESCE(total_balance, 0) - ? + ? "
                "WHERE id = ?",
                (previous_difference, difference, project_id),
            )

    def delete_record(self, project_id: int, record_date: str) -> None:
        """Deletes a day and takes its difference out of the cached balance."""
        with self._get_connection() as connection:
            row = connection.execute(
                "SELECT difference FROM records WHERE project_id = ? AND date = ?",
                (project_id, record_date),
            ).fetchone()
            if row is None:
                return
            connection.execute(
                "DELETE FROM records WHERE project_id = ? AND date = ?", (project_id, record_date)
            )
            connection.execute(
                "UPDATE projects SET total_balance = COALESCE(total_balance, 0) - ? WHERE id = ?",
                (row[0], project_id),
            )

    def clear_project_records(self, project_id: int) -> None:
        """Removes every record of a project and zeroes its balance."""
        with self._get_connection() as connection:
            connection.execute("DELETE FROM records WHERE project_id = ?", (project_id,))
            connection.execute("UPDATE projects SET total_balance = 0 WHERE id = ?", (project_id,))

    def get_records(
        self, project_id: int, limit: int | None = None, offset: int = 0
    ) -> list[Record]:
        """Records of a project, newest first. ``limit`` and ``offset`` paginate."""
        sql = "SELECT * FROM records WHERE project_id = ? ORDER BY date DESC"
        params: list[Any] = [project_id]
        if limit:
            sql += " LIMIT ? OFFSET ?"
            params += [limit, max(offset, 0)]
        return cast("list[Record]", self._fetch_all(sql, params))

    def get_record_by_date(self, project_id: int, record_date: str) -> Record | None:
        row = self._fetch_one(
            "SELECT * FROM records WHERE project_id = ? AND date = ?", (project_id, record_date)
        )
        return cast("Record | None", row)

    def count_records(self, project_id: int) -> int:
        return int(
            self._fetch_value("SELECT COUNT(*) FROM records WHERE project_id = ?", (project_id,))
        )

    def get_records_dict(self, project_id: int) -> dict[str, RecordData]:
        """Every record keyed by date, in the shape the export file uses."""
        return {
            record["date"]: {
                "hours": record["hours"],
                "minutes": record["minutes"],
                "difference": record["difference"],
            }
            for record in self.get_records(project_id)
        }

    def import_records(self, project_id: int, records_dict: dict[str, RecordData]) -> int:
        """Adds or replaces the given days and rebuilds the balance. Returns the day count."""
        for record_date, record in records_dict.items():
            self.upsert_record(
                project_id, record_date, record["hours"], record["minutes"], record["difference"]
            )
        self.recalculate_project_balance(project_id)
        return len(records_dict)

    # --- Balance cache ---

    def get_total_balance(self, project_id: int) -> int:
        """The cached balance, rebuilt from the records if the cache is empty."""
        cached = self._fetch_value("SELECT total_balance FROM projects WHERE id = ?", (project_id,))
        if cached is not None:
            return int(cached)
        return self.recalculate_project_balance(project_id)

    def recalculate_project_balance(self, project_id: int) -> int:
        """Rebuilds the cached balance of a project from its records."""
        with self._get_connection() as connection:
            total = connection.execute(
                "SELECT COALESCE(SUM(difference), 0) FROM records WHERE project_id = ?",
                (project_id,),
            ).fetchone()[0]
            connection.execute(
                "UPDATE projects SET total_balance = ? WHERE id = ?", (total, project_id)
            )
            return int(total)

    def recalculate_all_balances(self) -> None:
        for project in self.get_projects():
            self.recalculate_project_balance(project["id"])

    def reset_project_balance(self, project_id: int) -> None:
        """Marks the cached balance as unknown so the next read rebuilds it."""
        with self._get_connection() as connection:
            connection.execute(
                "UPDATE projects SET total_balance = NULL WHERE id = ?", (project_id,)
            )
