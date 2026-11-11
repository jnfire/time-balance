"""Shapes of the rows the database layer returns."""

from __future__ import annotations

from typing import TypedDict


class Project(TypedDict):
    """A work context: a name, a daily base and a cached balance in minutes."""

    id: int
    name: str
    base_hours: int
    base_minutes: int
    total_balance: int | None
    created_at: str


class Record(TypedDict):
    """One registered workday of a project."""

    id: int
    project_id: int
    date: str
    hours: int
    minutes: int
    difference: int
    created_at: str


class RecordData(TypedDict):
    """The part of a record that travels in an export file."""

    hours: int
    minutes: int
    difference: int
