"""time-balance: register workdays and keep an hour balance from the terminal."""

from .cli.main import main
from .config import VERSION

__version__ = VERSION

__all__ = ["VERSION", "main"]
