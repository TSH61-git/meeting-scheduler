"""
Person model representing a calendar participant.
"""

from typing import List
from .event import Event


class Person:
    """
    Represents a person with an immutable name and a managed list of events.

    - name is read-only (no setter)
    - events is returned as a copy to prevent external mutation
    - add_event/remove_event are the only ways to modify events
    """

    def __init__(self, name: str, events: List[Event] = None):
        self._name = name
        self._events: List[Event] = list(events) if events is not None else []

    @property
    def name(self) -> str:
        return self._name

    @property
    def events(self) -> List[Event]:
        """Return a copy of the events list to prevent external mutation."""
        return list(self._events)

    def __repr__(self) -> str:
        return f"Person(name='{self._name}', events_count={len(self._events)})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Person):
            return False
        return self._name == other._name

    def __hash__(self) -> int:
        return hash(self._name)

    def add_event(self, event: Event) -> None:
        """Add an event to the person's calendar."""
        self._events.append(event)

    def remove_event(self, event: Event) -> None:
        """Remove an event from the person's calendar."""
        if event in self._events:
            self._events.remove(event)

    def get_sorted_events(self) -> List[Event]:
        """Return all events sorted by start time."""
        return sorted(self._events)
