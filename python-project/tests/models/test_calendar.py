"""
Tests for the Calendar model.
"""

import pytest
from datetime import time

from io_comp.models import Calendar, Person, Event


class TestCalendar:

    def test_empty_calendar(self):
        """New calendar has no people."""
        calendar = Calendar()
        assert calendar.person_count() == 0

    def test_add_and_get_person(self):
        """add_person and get_person work correctly."""
        calendar = Calendar()
        person = Person("Alice")
        calendar.add_person(person)
        assert calendar.get_person("Alice") == person

    def test_get_nonexistent_person_returns_none(self):
        """get_person returns None for unknown name."""
        calendar = Calendar()
        assert calendar.get_person("Unknown") is None

    def test_remove_person(self):
        """remove_person removes an existing person and returns True."""
        calendar = Calendar()
        calendar.add_person(Person("Alice"))
        result = calendar.remove_person("Alice")
        assert result is True
        assert calendar.get_person("Alice") is None

    def test_remove_nonexistent_person_returns_false(self):
        """remove_person returns False for unknown name."""
        calendar = Calendar()
        assert calendar.remove_person("Unknown") is False

    def test_people_returns_copy(self):
        """Modifying the returned people dict does not affect the calendar."""
        calendar = Calendar()
        calendar.add_person(Person("Alice"))
        people_copy = calendar.people
        people_copy.clear()
        assert calendar.person_count() == 1

    def test_person_count(self):
        """person_count returns correct number of people."""
        calendar = Calendar()
        calendar.add_person(Person("Alice"))
        calendar.add_person(Person("Bob"))
        assert calendar.person_count() == 2

    def test_get_all_people(self):
        """get_all_people returns all added people."""
        calendar = Calendar()
        alice = Person("Alice")
        bob = Person("Bob")
        calendar.add_person(alice)
        calendar.add_person(bob)
        assert set(calendar.get_all_people()) == {alice, bob}

    def test_get_all_events(self):
        """get_all_events returns all events from all people."""
        calendar = Calendar()
        alice = Person("Alice")
        alice.add_event(Event("Meeting", time(8, 0), time(9, 0)))
        alice.add_event(Event("Lunch", time(13, 0), time(14, 0)))
        calendar.add_person(alice)
        assert len(calendar.get_all_events()) == 2

    def test_add_person_overwrites_existing(self):
        """Adding a person with the same name overwrites the existing one."""
        calendar = Calendar()
        calendar.add_person(Person("Alice"))
        new_alice = Person("Alice")
        new_alice.add_event(Event("Meeting", time(8, 0), time(9, 0)))
        calendar.add_person(new_alice)
        assert len(calendar.get_person("Alice").events) == 1
