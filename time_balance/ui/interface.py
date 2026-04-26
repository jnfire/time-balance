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

# --- TIMER COMPONENTS ---

def render_timer_display(total_hours: int, total_minutes: int, total_seconds: int, 
                         is_paused: bool, project_name: str, base_time_str: str, 
                         estimated_balance: str):
    """
    Renderiza el display bloqueante del timer.
    - Contador grande y visible (total)
    - Estado (ACTIVE / PAUSED)
    - Balance estimado actual vs base
    - Controles: [P]ause | [R]esume | [F]inish | [C]ancel
    """
    clear_screen()
    
    # Build the timer display
    status_label = "[bold yellow]⏸ PAUSED[/bold yellow]" if is_paused else "[bold green]● ACTIVE[/bold green]"
    timer_display = (
        f"[bold {COLOR_PRIMARY}]{project_name.upper()}[/bold {COLOR_PRIMARY}]\n\n"
        f"[bold]Time Tracked:[/bold]\n"
        f"[bold cyan]{total_hours:02d}h {total_minutes:02d}m {total_seconds:02d}s[/bold cyan]\n\n"
        f"[bold]Status:[/bold]\n{status_label}\n\n"
        f"[bold]Base Workday:[/bold] {base_time_str}\n"
        f"[bold]Balance:[/bold] {estimated_balance}"
    )
    
    panel = Panel(
        Align.center(timer_display),
        title="[bold]⏱ REAL-TIME TIMER[/bold]",
        border_style=COLOR_PRIMARY,
        box=box.ROUNDED,
        padding=(2, 4)
    )
    _console.print(panel)
    
    # Display controls
    _console.print("")
    _console.print("[bold magenta]Controls:[/bold magenta]")
    _console.print("  [bold cyan]P[/bold cyan] - Pause/Resume")
    _console.print("  [bold cyan]F[/bold cyan] - Finish & Save")
    _console.print("  [bold cyan]C[/bold cyan] - Cancel")
    _console.print("")

def render_timer_finalized_summary(total_hours: int, total_minutes: int, 
                                    balance_delta: int, project_name: str):
    """
    Resumen final al terminar timer.
    Muestra: tiempo total, diferencia con base, nuevo balance.
    """
    clear_screen()
    
    balance_color = COLOR_SUCCESS if balance_delta >= 0 else COLOR_ERROR
    balance_sign = "+" if balance_delta >= 0 else ""
    balance_delta_minutes_abs = abs(balance_delta)
    balance_delta_hours = balance_delta_minutes_abs // 60
    balance_delta_mins = balance_delta_minutes_abs % 60
    
    summary_content = (
        f"[bold green]✓ Timer Saved Successfully[/bold green]\n\n"
        f"[bold {COLOR_PRIMARY}]Project:[/bold {COLOR_PRIMARY}] {project_name.upper()}\n"
        f"[bold {COLOR_PRIMARY}]Total Time:[/bold {COLOR_PRIMARY}] {total_hours}h {total_minutes}m\n"
        f"[bold {COLOR_PRIMARY}]Balance Change:[/bold {COLOR_PRIMARY}] [{balance_color}]{balance_sign}{balance_delta_hours}h {balance_delta_mins}m[/{balance_color}]"
    )
    
    panel = Panel(
        Align.center(summary_content),
        title="[bold]⏱ TIMER COMPLETED[/bold]",
        border_style=COLOR_SUCCESS,
        box=box.ROUNDED,
        padding=(2, 4)
    )
    _console.print(panel)
    _console.print("")
