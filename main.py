#!/usr/bin/env python3
import sys
import pathlib

# Ensure the project root is in sys.path so we can import time_balance
# even if it's not installed yet.
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from time_balance.cli.main import main

if __name__ == "__main__":
    main()
