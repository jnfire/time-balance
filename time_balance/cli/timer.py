"""
Timer module for real-time workday tracking.
Provides an interactive interface to track work hours in real-time with pause/resume capabilities.
"""

import time
import sys
from datetime import date, datetime, timedelta
from typing import Optional
from .. import config
from ..database.manager import db
from ..ui import interface
from ..i18n.translator import translate, resolve_language


class TimerSession:
    """Represents an active timer session with in-memory state management."""
    
    def __init__(
        self,
        record_id: int,
        project_id: int,
        project_name: str,
        base_hours: int,
        base_minutes: int,
        initial_hours: int = 0,
        initial_minutes: int = 0
    ):
        """Initialize a new timer session."""
        self.record_id = record_id
        self.project_id = project_id
        self.project_name = project_name
        self.base_hours = base_hours
        self.base_minutes = base_minutes
        
        # Initial state from database
        self.initial_hours = initial_hours
        self.initial_minutes = initial_minutes
        
        # Timer state (in RAM)
        self.accumulated_seconds = 0  # Seconds added during this session (NOT including initial)
        self.is_paused = False
        self.pause_start_time = None  # When the pause started
        self.run_start_time = time.time()  # When the current run segment started
        
    def get_total_hours_minutes(self) -> tuple[int, int]:
        """
        Returns total hours and minutes (initial + current session elapsed).
        Accounts for running time as well as accumulated paused time.
        """
        current_session_elapsed = self.get_current_session_elapsed()
        total_seconds = (self.initial_hours * 3600 + self.initial_minutes * 60) + current_session_elapsed
        total_hours = total_seconds // 3600
        total_minutes = (total_seconds % 3600) // 60
        return total_hours, total_minutes
    
    def get_current_session_elapsed(self) -> int:
        """
        Returns seconds accumulated so far in this session run.
        If paused, returns the accumulated value without adding new time.
        """
        if self.is_paused:
            return self.accumulated_seconds
        
        # Calculate new elapsed time since run_start_time
        current_elapsed = int(time.time() - self.run_start_time)
        return self.accumulated_seconds + current_elapsed
    
    def pause(self):
        """Pause the timer."""
        if not self.is_paused:
            # When pausing, save the elapsed time from this run segment
            elapsed_this_segment = int(time.time() - self.run_start_time)
            self.accumulated_seconds += elapsed_this_segment
            self.is_paused = True
            self.pause_start_time = time.time()
    
    def resume(self):
        """Resume the timer."""
        if self.is_paused:
            self.is_paused = False
            self.run_start_time = time.time()  # Reset run start for next segment


def show_timer_menu(active_project_id: int):
    """
    Main timer menu interface.
    Displays a menu to start/resume timer or go back.
    """
    # Get language
    language_setting = db.get_setting("language", "auto")
    current_lang = resolve_language(language_setting)
    
    # Get project info
    project = db.get_project_by_id(active_project_id)
    if not project:
        interface.print_panel_message("❌ Project not found", "red")
        return
    
    # Get or create today's record
    record_info = db.get_or_create_today_record(active_project_id)
    
    # Show timer menu and wait for user choice
    while True:
        # Render menu
        interface.clear_screen()
        interface.render_header(translate("timer_title", lang=current_lang))
        
        current_time_str = f"{record_info['hours']}h {record_info['minutes']}m"
        interface.print_message(f"\n{translate('timer_current_time', lang=current_lang)}: {current_time_str}\n")
        
        # Determine menu options
        if record_info['hours'] == 0 and record_info['minutes'] == 0:
            menu_action = "1"
            menu_label = translate("timer_menu_start", lang=current_lang)
        else:
            menu_action = "1"
            menu_label = translate("timer_menu_resume", lang=current_lang)
        
        interface.print_message(f"  [bold blue]{menu_action}.[/bold blue] {menu_label}")
        interface.print_message(f"  [bold blue]V.[/bold blue] {translate('timer_menu_back', lang=current_lang)}")
        
        # Get user choice
        choice = interface.ask_string(f"\n{translate('choose_option', lang=current_lang)}", choices=["1", "v"]).lower()
        
        if choice == "1":
            # Start/Resume timer
            timer_session = TimerSession(
                record_id=record_info['record_id'],
                project_id=active_project_id,
                project_name=project['name'],
                base_hours=project['base_hours'],
                base_minutes=project['base_minutes'],
                initial_hours=record_info['hours'],
                initial_minutes=record_info['minutes']
            )
            
            # Run the timer loop
            _timer_loop(timer_session, project, current_lang)
            
            # Refresh record info in case it was updated
            record_info = db.get_record_by_date(active_project_id, str(date.today()))
            if not record_info:
                record_info = {'hours': 0, 'minutes': 0, 'record_id': 0}
        
        elif choice == "v":
            # Go back
            break


def _timer_loop(timer_session: TimerSession, project: dict, current_lang: str):
    """
    Main timer loop - simplified version with ENTER to control.
    
    States:
    - PAUSED (initial): Press ENTER to start, or V to go back
    - RUNNING: Press ENTER to pause
    - Persist to DB every 5 seconds
    """
    in_timer = True
    timer_is_running = False
    last_render_time = time.time()
    last_persist_time = time.time()
    
    try:
        while in_timer:
            now = time.time()
            
            # Render display every 1 second
            if now - last_render_time >= 1.0:
                _render_timer_display(timer_session, current_lang, timer_is_running)
                last_render_time = now
            
            # Persist to database every 5 seconds (even if paused)
            if now - last_persist_time >= 5.0:
                total_h, total_m = timer_session.get_total_hours_minutes()
                db.update_record_time(timer_session.record_id, total_h, total_m)
                last_persist_time = now
            
            # Check for user input (non-blocking)
            user_input = _get_nonblocking_input()
            
            if user_input:
                if user_input.lower() == '\r' or user_input == '\n':
                    # ENTER: Toggle between running and paused
                    if not timer_is_running:
                        # Start timer
                        timer_is_running = True
                        timer_session.is_paused = False
                        timer_session.run_start_time = time.time()
                    else:
                        # Pause timer
                        timer_is_running = False
                        timer_session.pause()
                
                elif user_input.lower() == 'v':
                    # Go back (saves automatically due to persist)
                    total_h, total_m = timer_session.get_total_hours_minutes()
                    db.update_record_time(timer_session.record_id, total_h, total_m)
                    in_timer = False
            
            # Check for midnight crossing
            if _has_crossed_midnight():
                # Auto-finalize at midnight
                total_h, total_m = timer_session.get_total_hours_minutes()
                db.finalize_timer(timer_session.record_id, total_h, total_m)
                interface.print_panel_message(translate("timer_auto_finalized", lang=current_lang), "blue")
                time.sleep(1)
                in_timer = False
            
            # Small sleep to prevent CPU spinning (50ms)
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        interface.print_panel_message("⏱ Timer interrupted", "yellow")


def _render_timer_display(timer_session: TimerSession, current_lang: str, is_running: bool):
    """Render the timer display with simplified UI."""
    # Get current elapsed time in this session
    current_session_elapsed = timer_session.get_current_session_elapsed()
    session_hours = current_session_elapsed // 3600
    session_minutes = (current_session_elapsed % 3600) // 60
    session_seconds = current_session_elapsed % 60
    
    # Get total (initial + session)
    total_h, total_m = timer_session.get_total_hours_minutes()
    
    # Calculate balance vs base
    base_total_sec = timer_session.base_hours * 3600 + timer_session.base_minutes * 60
    current_total_sec = total_h * 3600 + total_m * 60
    balance_sec = current_total_sec - base_total_sec
    balance_h = abs(balance_sec) // 3600
    balance_m = (abs(balance_sec) % 3600) // 60
    
    balance_str = f"{'+' if balance_sec >= 0 else '-'}{balance_h}h {balance_m}m"
    base_time_str = f"{timer_session.base_hours}h {timer_session.base_minutes}m"
    
    interface.render_timer_display_simplified(
        total_h, total_m, session_seconds,
        is_running,
        timer_session.project_name,
        base_time_str,
        balance_str,
        current_lang
    )


def _get_nonblocking_input() -> Optional[str]:
    """
    Get user input without blocking (non-blocking).
    Returns the input character or None if no input available.
    
    Unix: Uses select() with 0 timeout
    Windows: Uses msvcrt.kbhit()
    """
    try:
        # Unix implementation (Linux, macOS)
        import select
        if sys.stdin.isatty():
            # stdin is connected to terminal
            if select.select([sys.stdin], [], [], 0.0)[0]:
                char = sys.stdin.read(1)
                return char if char else None
    except (ImportError, AttributeError, OSError):
        pass
    
    # Windows fallback
    try:
        import msvcrt
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8', errors='ignore')
    except (ImportError, AttributeError, OSError):
        pass
    
    return None


def _wait_for_key_press():
    """Wait for user to press any key."""
    interface.print_message("Press any key to continue...")
    input()


def _has_crossed_midnight() -> bool:
    """Check if we've crossed into a new day."""
    current_date = date.today()
    next_midnight = datetime.combine(current_date + timedelta(days=1), datetime.min.time())
    return datetime.now() >= next_midnight
