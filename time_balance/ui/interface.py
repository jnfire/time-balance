"""Terminal rendering and prompts.

This is the only module that talks to Rich. Everything else passes plain strings,
tables and choices to it. Text typed by the user (project names, file paths) must go
through ``escape`` before it is placed inside a message, because Rich reads square
brackets as markup.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

# Universal palette: bright cyan is hard to read on light backgrounds, so 'blue' leads.
COLOR_PRIMARY = "blue"
COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_WARNING = "yellow"
COLOR_DIM = "dim"

Column = tuple[str, dict[str, Any]]

_console = Console()

__all__ = [
    "COLOR_DIM",
    "COLOR_ERROR",
    "COLOR_PRIMARY",
    "COLOR_SUCCESS",
    "COLOR_WARNING",
    "ask_confirm",
    "ask_string",
    "clear_screen",
    "escape",
    "print_message",
    "render_header",
    "render_info_line",
    "render_navigation_help",
    "render_section_title",
    "render_simple_table",
    "render_summary_panel",
    "render_table",
]


def clear_screen() -> None:
    _console.clear()


def print_message(text: str, style: str = "") -> None:
    """Prints a message, optionally wrapped in a Rich style."""
    _console.print(f"[{style}]{text}[/{style}]" if style else text)


def render_header(title: str) -> None:
    """A rule with the title in capitals, to open a screen."""
    _console.print("")
    _console.print(Rule(title.upper(), style=COLOR_PRIMARY))


def render_section_title(title: str) -> None:
    _console.print(f"\n [bold {COLOR_DIM}]>> {title.upper()}[/bold {COLOR_DIM}]")


def render_info_line(label: str, value: str) -> None:
    _console.print(f"  [{COLOR_DIM}]{label}:[/{COLOR_DIM}] [bold]{escape(value)}[/bold]")


def render_navigation_help(options: Sequence[tuple[str, str]]) -> None:
    """The available keys, one per line, between two rules."""
    _console.print("")
    _console.print(Rule(style=COLOR_DIM))
    for key, label in options:
        _console.print(f"  [bold {COLOR_PRIMARY}]{key}.[/bold {COLOR_PRIMARY}] {label}")
    _console.print(Rule(style=COLOR_DIM))


def render_summary_panel(title: str, rows: Sequence[tuple[str, str]], subtitle: str = "") -> None:
    """A centered panel with one ``label: value`` line per row.

    Values may carry Rich markup, for example a colored balance. Escape anything the
    user typed before passing it in.
    """
    content = "\n".join(
        f"[bold {COLOR_PRIMARY}]{label}:[/bold {COLOR_PRIMARY}] {value}" for label, value in rows
    )
    _console.print(
        Panel(
            Align.center(content),
            title=f"[bold]{title}[/bold]",
            subtitle=subtitle,
            border_style=COLOR_PRIMARY,
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def _build_table(columns: Sequence[Column], rows: Sequence[Sequence[str]], **options: Any) -> Table:
    table = Table(**options)
    for name, column_options in columns:
        table.add_column(name, **column_options)
    for row in rows:
        table.add_row(*row)
    return table


def render_table(title: str, columns: Sequence[Column], rows: Sequence[Sequence[str]]) -> None:
    """A table with blue headers. The title is only drawn when it is not empty."""
    table = _build_table(
        columns,
        rows,
        title=f"\n[bold]{title}[/bold]" if title else None,
        box=box.SIMPLE_HEAD,
        header_style=f"bold {COLOR_PRIMARY}",
    )
    _console.print(table)


def render_simple_table(columns: Sequence[Column], rows: Sequence[Sequence[str]]) -> None:
    """A table with dim headers and no title, for lists such as the projects."""
    _console.print(_build_table(columns, rows, box=box.SIMPLE, header_style=f"bold {COLOR_DIM}"))


def ask_string(message: str, default: str = "", choices: Sequence[str] | None = None) -> str:
    """Asks for a line of text. If ``choices`` is given, only those answers are accepted."""
    prompt_message = message if message.endswith(" ") or not message else f"{message} "
    return Prompt.ask(
        prompt_message,
        default=default,
        choices=list(choices) if choices is not None else None,
        show_choices=False,
        show_default=False,
        case_sensitive=False,
        console=_console,
    )


def ask_confirm(message: str, default: bool = False, yes: str = "y", no: str = "n") -> bool:
    """Asks a yes/no question. ``yes`` and ``no`` are the letters the user may type."""
    answer = Prompt.ask(
        message,
        choices=[yes, no],
        default=yes if default else no,
        case_sensitive=False,
        console=_console,
    )
    return answer.lower() == yes.lower()
