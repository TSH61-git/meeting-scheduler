"""
Event model representing a single calendar event.
"""

from datetime import time

from io_comp.exceptions import InvalidEventError


class Event:
    """
    Represents a single calendar event with a subject, start time, and end time.
    
    Attributes:
        subject (str): The name or description of the event.
        start_time (time): The start time of the event (HH:MM format).
        end_time (time): The end time of the event (HH:MM format).
    """

    def __init__(self, subject: str, start_time: time, end_time: time):
        """
        Initialize an Event.
        
        Args:
            subject: The event name/description.
            start_time: Event start time as a datetime.time object.
            end_time: Event end time as a datetime.time object.
            
        Raises:
            ValueError: If end_time is not after start_time.
        """
        if end_time <= start_time:
            raise InvalidEventError(f"Event end time ({end_time}) must be after start time ({start_time})")
        
        self.subject = subject
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self) -> str:
        """Return a string representation of the event."""
        return (
            f"Event(subject='{self.subject}', "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time})"
        )

    def __eq__(self, other) -> bool:
        """Check equality based on subject, start_time, and end_time."""
        if not isinstance(other, Event):
            return False
        return (
            self.subject == other.subject
            and self.start_time == other.start_time
            and self.end_time == other.end_time
        )

    def __lt__(self, other) -> bool:
        """Compare events by start time for sorting."""
        if not isinstance(other, Event):
            return NotImplemented
        return self.start_time < other.start_time

    def overlaps_with(self, other: "Event") -> bool:
        """
        Check if this event overlaps with another event.
        
        Args:
            other: Another Event instance.
            
        Returns:
            True if the events overlap, False otherwise.
        """
        return self.start_time < other.end_time and other.start_time < self.end_time

    def duration_minutes(self) -> int:
        """
        Calculate the duration of the event in minutes.
        
        Returns:
            Duration in minutes.
        """
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return end_minutes - start_minutes
