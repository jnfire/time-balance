from typing import List, Optional, Tuple, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.rule import Rule
from rich import box
from ..i18n.translator import translate

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
                         estimated_balance: str, current_lang: str = "en"):
    """
    Renderiza el display bloqueante del timer.
    - Contador grande y visible (total)
    - Estado (ACTIVE / PAUSED)
    - Balance estimado actual vs base
    - Controles: [P]ause | [R]esume | [F]inish | [C]ancel
    """
    clear_screen()
    
    # Get translated strings
    status_active = translate("timer_status_active", lang=current_lang)
    status_paused = translate("timer_status_paused", lang=current_lang)
    timer_title = translate("timer_title", lang=current_lang)
    controls_text = translate("timer_controls", lang=current_lang)
    
    # Build the timer display
    status_label = f"[bold yellow]{status_paused}[/bold yellow]" if is_paused else f"[bold green]{status_active}[/bold green]"
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
        title=f"[bold]⏱ {timer_title.upper()}[/bold]",
        border_style=COLOR_PRIMARY,
        box=box.ROUNDED,
        padding=(2, 4)
    )
    _console.print(panel)
    
    # Display controls
    _console.print("")
    _console.print(f"[bold magenta]{controls_text}[/bold magenta]")
    _console.print("")

def render_timer_display_simplified(total_hours: int, total_minutes: int, total_seconds: int, 
                                    is_running: bool, project_name: str, base_time_str: str, 
                                    estimated_balance: str, current_lang: str = "en"):
    """
    Renderiza el display simplificado del timer con ENTER como control principal.
    
    Estados:
    - RUNNING: Muestra "Press ENTER to pause"
    - PAUSED: Muestra "Press ENTER to start"
    """
    clear_screen()
    
    # Get translated strings
    status_active = translate("timer_status_active", lang=current_lang)
    status_paused = translate("timer_status_paused", lang=current_lang)
    timer_title = translate("timer_title", lang=current_lang)
    press_enter_pause = translate("timer_press_enter_to_pause", lang=current_lang)
    press_enter_start = translate("timer_press_enter_to_start", lang=current_lang)
    
    # Build the timer display
    status_label = f"[bold green]{status_active}[/bold green]" if is_running else f"[bold yellow]{status_paused}[/bold yellow]"
    instruction_text = press_enter_pause if is_running else press_enter_start
    
    timer_display = (
        f"[bold {COLOR_PRIMARY}]{project_name.upper()}[/bold {COLOR_PRIMARY}]\n\n"
        f"[bold]Total Time:[/bold]\n"
        f"[bold cyan]{total_hours:02d}h {total_minutes:02d}m {total_seconds:02d}s[/bold cyan]\n\n"
        f"[bold]Status:[/bold]\n{status_label}\n\n"
        f"[bold]Base Workday:[/bold] {base_time_str}\n"
        f"[bold]Balance:[/bold] {estimated_balance}\n\n"
        f"[bold magenta]{instruction_text}[/bold magenta]\n"
        f"[bold magenta]V - Go back[/bold magenta]"
    )
    
    panel = Panel(
        Align.center(timer_display),
        title=f"[bold]⏱ {timer_title.upper()}[/bold]",
        border_style=COLOR_PRIMARY,
        box=box.ROUNDED,
        padding=(2, 4)
    )
    _console.print(panel)

def render_timer_running(total_hours: int, total_minutes: int, total_seconds: int,
                        project_name: str, base_time_str: str, 
                        estimated_balance: str, current_lang: str = "en"):
    """
    Renderiza el display del timer en ejecución.
    Balance en verde si positivo, rojo si negativo.
    Añade etiquetas explicativas para cada dato.
    """
    clear_screen()
    
    # Get translated strings
    timer_title = translate("timer_title", lang=current_lang)
    press_to_stop = translate("timer_press_enter_to_pause", lang=current_lang).replace("pause", "stop")
    status_active = translate("timer_status_active", lang=current_lang)
    label_elapsed = translate("timer_label_elapsed", lang=current_lang)
    label_status = translate("timer_label_status", lang=current_lang)
    label_balance = translate("timer_label_balance", lang=current_lang)
    
    # Determine balance color based on sign
    is_negative = estimated_balance.startswith('-')
    balance_color = COLOR_ERROR if is_negative else COLOR_SUCCESS
    
    timer_display = (
        f"[bold {COLOR_PRIMARY}]{project_name.upper()}[/bold {COLOR_PRIMARY}]\n\n"
        f"[dim]{label_elapsed}:[/dim] [bold blue]{total_hours:02d}h {total_minutes:02d}m {total_seconds:02d}s[/bold blue]\n"
        f"[dim]{label_status}:[/dim] [bold {COLOR_ACCENT}]{status_active}[/bold {COLOR_ACCENT}]\n"
        f"[dim]{label_balance}:[/dim] [bold {balance_color}]{estimated_balance}[/bold {balance_color}]\n\n"
        f"[bold {COLOR_ACCENT}]{press_to_stop}[/bold {COLOR_ACCENT}]"
    )
    
    panel = Panel(
        Align.center(timer_display),
        title=f"[bold]⏱ {timer_title.upper()}[/bold]",
        border_style=COLOR_PRIMARY,
        box=box.ROUNDED,
        padding=(1, 2)
    )
    _console.print(panel)

def render_timer_menu_with_display(hours: int, minutes: int, seconds: int,
                                   project_name: str, base_time_str: str,
                                   balance_str: str, current_lang: str = "en"):
    """
    Renderiza el display del timer en el menú (pausa).
    Muestra el contador grande con status PAUSED.
    Balance en verde si positivo, rojo si negativo.
    Añade etiquetas explicativas para cada dato.
    """
    clear_screen()
    
    # Get translated strings
    timer_title = translate("timer_title", lang=current_lang)
    status_paused = translate("timer_status_paused", lang=current_lang)
    label_elapsed = translate("timer_label_elapsed", lang=current_lang)
    label_status = translate("timer_label_status", lang=current_lang)
    label_balance = translate("timer_label_balance", lang=current_lang)
    
    # Determine balance color based on sign
    is_negative = balance_str.startswith('-')
    balance_color = COLOR_ERROR if is_negative else COLOR_SUCCESS
    
    timer_display = (
        f"[bold {COLOR_PRIMARY}]{project_name.upper()}[/bold {COLOR_PRIMARY}]\n\n"
        f"[dim]{label_elapsed}:[/dim] [bold blue]{hours:02d}h {minutes:02d}m {seconds:02d}s[/bold blue]\n"
        f"[dim]{label_status}:[/dim] [bold {COLOR_ACCENT}]{status_paused}[/bold {COLOR_ACCENT}]\n"
        f"[dim]{label_balance}:[/dim] [bold {balance_color}]{balance_str}[/bold {balance_color}]"
    )
    
    panel = Panel(
        Align.center(timer_display),
        title=f"[bold]⏱ {timer_title.upper()}[/bold]",
        border_style=COLOR_PRIMARY,
        box=box.ROUNDED,
        padding=(1, 2)
    )
    _console.print(panel)

def render_timer_finalized_summary(total_hours: int, total_minutes: int, 
                                    balance_delta: int, project_name: str, current_lang: str = "en"):
    """
    Resumen final al terminar timer.
    Muestra: tiempo total, diferencia con base, nuevo balance.
    """
    clear_screen()
    
    # Get translated strings
    finalized_text = translate("timer_finalized", lang=current_lang)
    finalized_summary_template = translate("timer_finalized_summary", lang=current_lang)
    
    balance_color = COLOR_SUCCESS if balance_delta >= 0 else COLOR_ERROR
    balance_sign = "+" if balance_delta >= 0 else ""
    balance_delta_minutes_abs = abs(balance_delta)
    balance_delta_hours = balance_delta_minutes_abs // 60
    balance_delta_mins = balance_delta_minutes_abs % 60
    
    # Format the summary using the translation template
    summary_content = (
        f"[bold green]{finalized_text}[/bold green]\n\n"
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
