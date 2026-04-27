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
    Displays timer counter with options to start/resume or go back.
    """
    # Get language
    language_setting = db.get_setting("language", "auto")
    current_lang = resolve_language(language_setting)
    
    # Get project info
    project = db.get_project_by_id(active_project_id)
    if not project:
        interface.print_panel_message("❌ Project not found", "red")
        return
    
    # Show timer menu loop
    while True:
        # Get or create today's record (refresh each iteration)
        record_info = db.get_or_create_today_record(active_project_id)
        
        # Calculate balance for display
        base_total_sec = project['base_hours'] * 3600 + project['base_minutes'] * 60
        current_total_sec = record_info['hours'] * 3600 + record_info['minutes'] * 60
        balance_sec = current_total_sec - base_total_sec
        balance_h = abs(balance_sec) // 3600
        balance_m = (abs(balance_sec) % 3600) // 60
        balance_str = f"{'+' if balance_sec >= 0 else '-'}{balance_h}h {balance_m}m"
        base_time_str = f"{project['base_hours']}h {project['base_minutes']}m"
        
        # Render timer display with menu options
        interface.render_timer_menu_with_display(
            hours=record_info['hours'],
            minutes=record_info['minutes'],
            seconds=0,
            project_name=project['name'],
            base_time_str=base_time_str,
            balance_str=balance_str,
            current_lang=current_lang
        )
        
        # Determine menu option label
        if record_info['hours'] == 0 and record_info['minutes'] == 0:
            menu_label = translate("timer_menu_start", lang=current_lang)
        else:
            menu_label = translate("timer_menu_resume", lang=current_lang)
        
        # Show menu options
        interface.print_message(f"\n  [bold blue]1.[/bold blue] {menu_label}")
        interface.render_navigation_help([("V", translate("timer_menu_back", lang=current_lang))])
        
        # Get user choice
        choice = interface.ask_string(f"\n{translate('choose_option', lang=current_lang)}", choices=["1", "v"]).lower()
        
        if choice == "1":
            # Start/Resume timer - run until ENTER is pressed
            timer_session = TimerSession(
                record_id=record_info['record_id'],
                project_id=active_project_id,
                project_name=project['name'],
                base_hours=project['base_hours'],
                base_minutes=project['base_minutes'],
                initial_hours=record_info['hours'],
                initial_minutes=record_info['minutes']
            )
            
            # Run the timer loop (blocking until ENTER)
            _timer_loop(timer_session, current_lang)
            
            # Loop continues, refreshes on next iteration
        
        elif choice == "v":
            # Go back to main menu
            break


def _timer_loop(timer_session: TimerSession, current_lang: str):
    """
    Main timer loop - simplified version.
    
    Runs until ENTER is pressed, then stops and saves automatically.
    Auto-persists to DB every 60 seconds.
    """
    timer_is_running = True
    last_render_time = time.time()
    last_persist_time = time.time()
    
    try:
        while timer_is_running:
            now = time.time()
            
            # Render display every 1 second
            if now - last_render_time >= 1.0:
                _render_timer_display(timer_session, current_lang)
                last_render_time = now
            
            # Persist to database every 60 seconds
            if now - last_persist_time >= 60.0:
                total_h, total_m = timer_session.get_total_hours_minutes()
                db.update_record_time(timer_session.record_id, total_h, total_m)
                last_persist_time = now
            
            # Check for user input (non-blocking)
            user_input = _get_nonblocking_input()
            
            if user_input:
                if user_input.lower() == '\r' or user_input == '\n':
                    # ENTER pressed - stop timer and save immediately
                    total_h, total_m = timer_session.get_total_hours_minutes()
                    db.update_record_time(timer_session.record_id, total_h, total_m)
                    timer_is_running = False
            
            # Check for midnight crossing
            if _has_crossed_midnight():
                # Auto-finalize at midnight
                total_h, total_m = timer_session.get_total_hours_minutes()
                db.finalize_timer(timer_session.record_id, total_h, total_m)
                interface.print_panel_message(translate("timer_auto_finalized", lang=current_lang), "blue")
                time.sleep(1)
                timer_is_running = False
            
            # Small sleep to prevent CPU spinning (50ms)
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        # Save before exiting on interrupt
        total_h, total_m = timer_session.get_total_hours_minutes()
        db.update_record_time(timer_session.record_id, total_h, total_m)
        interface.print_panel_message("⏱ Timer interrupted", "yellow")


def _render_timer_display(timer_session: TimerSession, current_lang: str):
    """Render the timer display - simplified version."""
    # Get total time
    total_h, total_m = timer_session.get_total_hours_minutes()
    
    # Get elapsed time in this session (for seconds display)
    current_session_elapsed = timer_session.get_current_session_elapsed()
    session_seconds = current_session_elapsed % 60
    
    # Calculate balance vs base
    base_total_sec = timer_session.base_hours * 3600 + timer_session.base_minutes * 60
    current_total_sec = total_h * 3600 + total_m * 60
    balance_sec = current_total_sec - base_total_sec
    balance_h = abs(balance_sec) // 3600
    balance_m = (abs(balance_sec) % 3600) // 60
    
    balance_str = f"{'+' if balance_sec >= 0 else '-'}{balance_h}h {balance_m}m"
    base_time_str = f"{timer_session.base_hours}h {timer_session.base_minutes}m"
    
    interface.render_timer_running(
        total_h, total_m, session_seconds,
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
