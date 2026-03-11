"""
Person model representing a calendar participant.
"""

from typing import List
from .event import Event


class Person:
    """
    Represents a person with a name and list of calendar events.
    
    Attributes:
        name (str): The person's name.
        events (List[Event]): List of events on the person's calendar.
    """

    def __init__(self, name: str, events: List[Event] = None):
        """
        Initialize a Person.
        
        Args:
            name: The person's name.
            events: Optional list of Event objects. Defaults to empty list.
        """
        self.name = name
        self.events = events if events is not None else []

    def __repr__(self) -> str:
        """Return a string representation of the person."""
        return f"Person(name='{self.name}', events_count={len(self.events)})"

    def __eq__(self, other) -> bool:
        """Check equality based on name."""
        if not isinstance(other, Person):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Make Person hashable so it can be used in sets/dicts."""
        return hash(self.name)

    def add_event(self, event: Event) -> None:
        """
        Add an event to the person's calendar.
        
        Args:
            event: The Event to add.
        """
        self.events.append(event)

    def remove_event(self, event: Event) -> None:
        """
        Remove an event from the person's calendar.
        
        Args:
            event: The Event to remove.
        """
        if event in self.events:
            self.events.remove(event)

    def get_sorted_events(self) -> List[Event]:
        """
        Get all events sorted by start time.
        
        Returns:
            A sorted list of events.
        """
        return sorted(self.events)
