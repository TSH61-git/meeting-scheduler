"""
Event model representing a single calendar event.
"""

from dataclasses import dataclass
from datetime import time

from io_comp.exceptions import InvalidEventError


@dataclass(frozen=True)
class Event:
    """Immutable calendar event. Fields cannot be modified after creation."""

    subject: str
    start_time: time
    end_time: time

    def __post_init__(self) -> None:
        """Validate that end_time is after start_time."""
        if self.end_time <= self.start_time:
            raise InvalidEventError(
                f"Event end time ({self.end_time}) must be after start time ({self.start_time})"
            )

    def __lt__(self, other: "Event") -> bool:
        """Compare events by start time for sorting."""
        return self.start_time < other.start_time

    def overlaps_with(self, other: "Event") -> bool:
        """Return True if this event overlaps with another."""
        return self.start_time < other.end_time and other.start_time < self.end_time

    def duration_minutes(self) -> int:
        """Return the duration of the event in minutes."""
        return (self.end_time.hour * 60 + self.end_time.minute) - \
               (self.start_time.hour * 60 + self.start_time.minute)
