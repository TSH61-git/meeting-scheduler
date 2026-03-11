"""
Calendar model representing the entire calendar system with multiple people.
"""

from datetime import time
from typing import List, Dict, Optional
from .person import Person
from .event import Event


class Calendar:
    """
    Represents a calendar containing multiple people and their events.
    Provides methods to manage and query the calendar.
    
    Attributes:
        people (Dict[str, Person]): Dictionary mapping person names to Person objects.
        working_hours_start (time): The start of the working day (default 07:00).
        working_hours_end (time): The end of the working day (default 19:00).
    """

    def __init__(
        self,
        working_hours_start: time = None,
        working_hours_end: time = None
    ):
        """
        Initialize a Calendar.
        
        Args:
            working_hours_start: Start time of the working day. Defaults to 07:00.
            working_hours_end: End time of the working day. Defaults to 19:00.
        """
        self.people: Dict[str, Person] = {}
        self.working_hours_start = working_hours_start or time(7, 0)
        self.working_hours_end = working_hours_end or time(19, 0)

    def __repr__(self) -> str:
        """Return a string representation of the calendar."""
        return (
            f"Calendar(people_count={len(self.people)}, "
            f"working_hours={self.working_hours_start}-{self.working_hours_end})"
        )

    def add_person(self, person: Person) -> None:
        """
        Add a person to the calendar.
        
        Args:
            person: The Person to add.
        """
        self.people[person.name] = person

    def get_person(self, name: str) -> Optional[Person]:
        """
        Retrieve a person by name.
        
        Args:
            name: The person's name.
            
        Returns:
            The Person object, or None if not found.
        """
        return self.people.get(name)

    def remove_person(self, name: str) -> bool:
        """
        Remove a person from the calendar by name.
        
        Args:
            name: The person's name.
            
        Returns:
            True if removed, False if not found.
        """
        if name in self.people:
            del self.people[name]
            return True
        return False

    def get_all_people(self) -> List[Person]:
        """
        Get all people in the calendar.
        
        Returns:
            A list of all Person objects.
        """
        return list(self.people.values())

    def get_all_events(self) -> List[Event]:
        """
        Get all events from all people.
        
        Returns:
            A list of all Event objects.
        """
        all_events = []
        for person in self.people.values():
            all_events.extend(person.events)
        return all_events

    def validate_working_hours(self, event_time: time) -> bool:
        """
        Check if a time is within working hours.
        
        Args:
            event_time: The time to validate.
            
        Returns:
            True if within working hours, False otherwise.
        """
        return self.working_hours_start <= event_time < self.working_hours_end

    def person_count(self) -> int:
        """
        Get the count of people in the calendar.
        
        Returns:
            Number of people.
        """
        return len(self.people)
