#!/usr/bin/env python3
"""Run time-balance from a checkout, without installing it."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from time_balance.cli.main import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
