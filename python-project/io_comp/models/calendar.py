"""
Calendar model representing the entire calendar system with multiple people.
"""

from typing import Dict, List, Optional
from .person import Person
from .event import Event


class Calendar:
    """
    Represents a calendar containing multiple people and their events.

    - people is returned as a copy to prevent external mutation
    - add_person/remove_person are the only ways to modify the people dict
    - working hours are managed externally by WorkingHoursConfig
    """

    def __init__(self) -> None:
        self._people: Dict[str, Person] = {}

    def __repr__(self) -> str:
        return f"Calendar(people_count={len(self._people)})"

    @property
    def people(self) -> Dict[str, Person]:
        """Return a copy of the people dict to prevent external mutation."""
        return dict(self._people)

    def add_person(self, person: Person) -> None:
        """Add a person to the calendar."""
        self._people[person.name] = person

    def get_person(self, name: str) -> Optional[Person]:
        """Return the person with the given name, or None if not found."""
        return self._people.get(name)

    def remove_person(self, name: str) -> bool:
        """Remove a person by name. Returns True if removed, False if not found."""
        if name in self._people:
            del self._people[name]
            return True
        return False

    def get_all_people(self) -> List[Person]:
        """Return all people in the calendar."""
        return list(self._people.values())

    def get_all_events(self) -> List[Event]:
        """Return all events from all people."""
        return [event for person in self._people.values() for event in person.events]

    def person_count(self) -> int:
        """Return the number of people in the calendar."""
        return len(self._people)
