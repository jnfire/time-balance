from typing import List, Optional, Tuple, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich import box

# Initialize the global console
_console = Console()

def clear_screen():
    """Clears the terminal screen."""
    _console.clear()

def print_message(text: str, style: str = ""):
    """Prints a message to the console with optional styling."""
    _console.print(f"[{style}]{text}[/{style}]" if style else text)

def render_dashboard(project_name: str, base_hours: int, base_minutes: int, balance_fmt: str, balance_color: str, version: str, labels: dict):
    """Renders the main dashboard header."""
    dashboard_content = (
        f"[bold cyan]{labels['project']}:[/bold cyan] {project_name.upper()}\n"
        f"[bold cyan]{labels['base_day']}:[/bold cyan] {base_hours}h {base_minutes}m\n"
        f"[bold cyan]{labels['balance']}:[/bold cyan] [{balance_color}]{balance_fmt}[/{balance_color}]"
    )
    
    panel = Panel(
        Align.center(dashboard_content),
        title=f"[bold]{labels['dashboard_title']}[/bold]",
        subtitle=f"v{version}",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    _console.print(panel)

def render_table(title: str, columns: List[Tuple[str, dict]], rows: List[List[Any]]):
    """Renders a data table."""
    table = Table(title=f"\n[bold]{title}[/bold]", box=box.SIMPLE_HEAD, header_style="bold cyan")
    
    for col_name, col_args in columns:
        table.add_column(col_name, **col_args)
    
    for row in rows:
        table.add_row(*row)
    
    _console.print(table)

def render_simple_table(columns: List[Tuple[str, dict]], rows: List[List[Any]]):
    """Renders a simple table without title (e.g., for project list)."""
    table = Table(box=box.SIMPLE, header_style="bold dim")
    
    for col_name, col_args in columns:
        table.add_column(col_name, **col_args)
    
    for row in rows:
        table.add_row(*row)
    
    _console.print(table)

def ask_string(message: str, default: str = "", choices: Optional[List[str]] = None) -> str:
    """Requests a string input from the user."""
    return Prompt.ask(message, default=default, choices=choices, show_choices=False, console=_console)

def ask_confirm(message: str, default: bool = False) -> bool:
    """Requests a yes/no confirmation from the user."""
    return Confirm.ask(message, default=default, console=_console)

def print_panel_message(message: str, style: str = "blue"):
    """Prints a message inside a simple panel."""
    _console.print(Panel(message, border_style=style))
