"""Access to the application database.

The database is opened the first time it is needed, not when the package is
imported, so ``time-balance --version`` and the tests never touch the disk by
accident. Tests install their own instance with ``set_database``.
"""

from __future__ import annotations

from .. import config
from .manager import DatabaseManager

_database: DatabaseManager | None = None


def get_database() -> DatabaseManager:
    """Returns the shared database, opening it on first use."""
    global _database
    if _database is None:
        _database = DatabaseManager(config.DATABASE_PATH)
    return _database


def set_database(database: DatabaseManager | None) -> None:
    """Replaces the shared database. Pass ``None`` to forget it."""
    global _database
    _database = database


__all__ = ["DatabaseManager", "get_database", "set_database"]
