from typing import List, Optional, Tuple, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.rule import Rule
from rich import box

# --- UI CONFIGURATION (Universal Palette) ---
# We avoid bright cyan as it's hard to read on light backgrounds.
# 'blue' and 'magenta' are generally safer across themes.
COLOR_PRIMARY = "blue"
COLOR_ACCENT = "magenta"
COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_WARNING = "yellow"
COLOR_DIM = "dim"

# Initialize the global console
_console = Console()

def clear_screen():
    """Clears the terminal screen."""
    _console.clear()

def print_message(text: str, style: str = ""):
    """Prints a message to the console with optional styling."""
    _console.print(f"[{style}]{text}[/{style}]" if style else text)

def render_header(title: str):
    """Renders a consistent header for submenus."""
    _console.print("")
    _console.print(Rule(title.upper(), style=COLOR_PRIMARY))

def render_section_title(title: str):
    """Renders a section divider inside a menu."""
    _console.print(f"\n [bold {COLOR_DIM}]>> {title.upper()}[/bold {COLOR_DIM}]")

def render_info_line(label: str, value: str):
    """Renders a consistent key-value information line."""
    _console.print(f"  [{COLOR_DIM}]{label}:[/{COLOR_DIM}] [bold]{value}[/bold]")

def render_navigation_help(options: List[Tuple[str, str]]):
    """Renders navigation help options vertically, enclosed by rules."""
    _console.print("")
    _console.print(Rule(style=COLOR_DIM))
    for key, label in options:
        _console.print(f"  [bold {COLOR_PRIMARY}]{key}.[/bold {COLOR_PRIMARY}] {label}")
    _console.print(Rule(style=COLOR_DIM))

def render_dashboard(project_name: str, base_hours: int, base_minutes: int, balance_fmt: str, balance_color: str, version: str, labels: dict):
    """Renders the main dashboard header."""
    dashboard_content = (
        f"[bold {COLOR_PRIMARY}]{labels['project']}:[/bold {COLOR_PRIMARY}] {project_name.upper()}\n"
        f"[bold {COLOR_PRIMARY}]{labels['base_day']}:[/bold {COLOR_PRIMARY}] {base_hours}h {base_minutes}m\n"
        f"[bold {COLOR_PRIMARY}]{labels['balance']}:[/bold {COLOR_PRIMARY}] [{balance_color}]{balance_fmt}[/{balance_color}]"
    )
    
    panel = Panel(
        Align.center(dashboard_content),
        title=f"[bold]{labels['dashboard_title']}[/bold]",
        subtitle=f"v{version}",
        border_style=COLOR_PRIMARY,
        box=box.ROUNDED,
        padding=(1, 2)
    )
    _console.print(panel)

def render_table(title: str, columns: List[Tuple[str, dict]], rows: List[List[Any]]):
    """Renders a data table. Only adds title if not empty."""
    table_title = f"\n[bold]{title}[/bold]" if title else None
    table = Table(title=table_title, box=box.SIMPLE_HEAD, header_style=f"bold {COLOR_PRIMARY}")
    
    for col_name, col_args in columns:
        table.add_column(col_name, **col_args)
    
    for row in rows:
        table.add_row(*row)
    
    _console.print(table)

def render_simple_table(columns: List[Tuple[str, dict]], rows: List[List[Any]]):
    """Renders a simple table without title (e.g., for project list)."""
    table = Table(box=box.SIMPLE, header_style=f"bold {COLOR_DIM}")
    
    for col_name, col_args in columns:
        table.add_column(col_name, **col_args)
    
    for row in rows:
        table.add_row(*row)
    
    _console.print(table)

def ask_string(message: str, default: str = "", choices: Optional[List[str]] = None) -> str:
    """Requests a string input from the user without automatic Rich decorations."""
    prompt_message = message if message.endswith(" ") or not message else f"{message} "
    
    return Prompt.ask(
        prompt_message, 
        default=default, 
        choices=choices, 
        show_choices=False, 
        show_default=False, 
        case_sensitive=False,
        console=_console
    )

def ask_confirm(message: str, default: bool = False) -> bool:
    """Requests a yes/no confirmation from the user."""
    return Confirm.ask(message, default=default, console=_console)

def print_panel_message(message: str, style: str = "blue"):
    """Prints a message inside a simple panel."""
    _console.print(Panel(message, border_style=style))
