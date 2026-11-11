"""Shared test tools: a temporary database and a scripted terminal."""

from __future__ import annotations

import contextlib
import io
import pathlib
import tempfile
import unittest
from collections.abc import Iterator, Sequence
from unittest import mock

from rich.console import Console

from time_balance.cli.context import Context
from time_balance.database import set_database
from time_balance.database.manager import DatabaseManager
from time_balance.ui import interface as ui


class DatabaseTestCase(unittest.TestCase):
    """Gives each test its own database, and a context in English for the flows."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_path = pathlib.Path(self._tmp.name)
        self.db = DatabaseManager(self.tmp_path / "test.db")
        set_database(self.db)
        self.addCleanup(set_database, None)
        self.ctx = Context(self.db, "en")
        self.project_id = self.db.get_active_project_id()


class ScriptedTerminal:
    """Replaces the prompts with canned answers and records what is printed.

    Every question asked consumes the next answer. An empty answer takes the
    default. Running out of answers, or giving an answer the prompt would not
    accept, fails the test, so a flow cannot silently wait for input. An exception
    in the list is raised instead of returned, to simulate Ctrl+C.
    """

    def __init__(self, answers: Sequence[str | BaseException] = ()) -> None:
        self.answers: list[str | BaseException] = list(answers)
        self.questions: list[str] = []
        self.console = Console(record=True, file=io.StringIO(), width=100, force_terminal=False)

    def _next(self, message: str) -> str:
        self.questions.append(message)
        if not self.answers:
            raise AssertionError(f"The flow asked for more input than scripted: {message!r}")
        answer = self.answers.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        return answer

    def ask_string(
        self, message: str, default: str = "", choices: Sequence[str] | None = None
    ) -> str:
        answer = self._next(message) or default
        if choices is not None and answer.lower() not in [choice.lower() for choice in choices]:
            raise AssertionError(f"{answer!r} is not one of {list(choices)} for {message!r}")
        return answer

    def ask_confirm(
        self, message: str, default: bool = False, yes: str = "y", no: str = "n"
    ) -> bool:
        answer = self._next(message) or (yes if default else no)
        return answer.lower() == yes.lower()

    @property
    def output(self) -> str:
        """Everything printed so far, as plain text."""
        return self.console.export_text(clear=False)

    @contextlib.contextmanager
    def active(self) -> Iterator[ScriptedTerminal]:
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(ui, "_console", self.console))
            stack.enter_context(mock.patch.object(ui, "ask_string", self.ask_string))
            stack.enter_context(mock.patch.object(ui, "ask_confirm", self.ask_confirm))
            stack.enter_context(mock.patch.object(ui, "clear_screen", lambda: None))
            yield self
        if self.answers:
            raise AssertionError(f"Scripted answers left unused: {self.answers}")
