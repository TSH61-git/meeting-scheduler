"""
Repository interface for calendar data access.
"""

from typing import Protocol
from io_comp.models import Calendar


class CalendarRepository(Protocol):
    """Abstract interface for loading calendar data from any source."""

    def load(self) -> Calendar: ...
