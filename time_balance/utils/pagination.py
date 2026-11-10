"""Page arithmetic for the history screen."""

from __future__ import annotations


def page_count(total_items: int, page_size: int) -> int:
    """Number of pages needed for ``total_items`` (0 when there is nothing to show)."""
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    return -(-total_items // page_size)


def clamp_page(page_index: int, total_items: int, page_size: int) -> int:
    """Keeps a page index inside the existing pages (for example after deleting the last row)."""
    return max(0, min(page_index, page_count(total_items, page_size) - 1))
