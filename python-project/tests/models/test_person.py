"""
Tests for the Person model.
"""

import pytest
from datetime import time

from io_comp.models import Person, Event


class TestPerson:

    def test_person_creation(self):
        """Person is created with correct name and empty events."""
        person = Person("Alice")
        assert person.name == "Alice"
        assert person.events == []

    def test_name_is_read_only(self):
        """Person name cannot be modified after creation."""
        person = Person("Alice")
        with pytest.raises(AttributeError):
            person.name = "Bob"

    def test_events_returns_copy(self):
        """Modifying the returned events list does not affect the person."""
        person = Person("Alice")
        person.add_event(Event("Meeting", time(8, 0), time(9, 0)))
        events_copy = person.events
        events_copy.clear()
        assert len(person.events) == 1

    def test_add_event(self):
        """add_event correctly adds an event."""
        person = Person("Alice")
        event = Event("Meeting", time(8, 0), time(9, 0))
        person.add_event(event)
        assert event in person.events

    def test_remove_event(self):
        """remove_event correctly removes an existing event."""
        person = Person("Alice")
        event = Event("Meeting", time(8, 0), time(9, 0))
        person.add_event(event)
        person.remove_event(event)
        assert event not in person.events

    def test_remove_nonexistent_event(self):
        """Removing a non-existent event does not raise."""
        person = Person("Alice")
        event = Event("Meeting", time(8, 0), time(9, 0))
        person.remove_event(event)  # should not raise

    def test_get_sorted_events(self):
        """get_sorted_events returns events sorted by start time."""
        person = Person("Alice")
        person.add_event(Event("Late", time(14, 0), time(15, 0)))
        person.add_event(Event("Early", time(8, 0), time(9, 0)))
        sorted_events = person.get_sorted_events()
        assert sorted_events[0].start_time == time(8, 0)
        assert sorted_events[1].start_time == time(14, 0)

    def test_equality_by_name(self):
        """Two persons with the same name are equal."""
        assert Person("Alice") == Person("Alice")

    def test_inequality_by_name(self):
        """Two persons with different names are not equal."""
        assert Person("Alice") != Person("Bob")

    def test_hashable(self):
        """Person can be used in a set."""
        persons = {Person("Alice"), Person("Bob"), Person("Alice")}
        assert len(persons) == 2
