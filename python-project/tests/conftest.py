"""
Shared fixtures and helpers for all tests.
"""

import pytest
from datetime import time

from io_comp.models import Calendar, Person, Event
from io_comp.services import CalendarService


class FakeCalendarRepository:
    """In-memory repository for testing - no CSV files needed."""

    def __init__(self, calendar: Calendar):
        self._calendar = calendar

    def load(self) -> Calendar:
        return self._calendar


def make_service(calendar: Calendar) -> CalendarService:
    """Helper to create a CalendarService with a FakeCalendarRepository."""
    return CalendarService(FakeCalendarRepository(calendar))


@pytest.fixture
def empty_calendar() -> Calendar:
    """Empty calendar with no people."""
    return Calendar()


@pytest.fixture
def example_calendar() -> Calendar:
    """
    Example calendar from README:
    Alice: 08:00-09:30, 13:00-14:00, 16:00-17:00
    Jack:  08:00-08:50, 09:00-09:40, 13:00-14:00, 16:00-17:00
    Bob:   08:00-09:30, 09:30-09:40, 10:00-11:30, 13:00-15:00, 16:00-17:00
    """
    calendar = Calendar()

    alice = Person("Alice")
    alice.add_event(Event("Morning meeting", time(8, 0), time(9, 30)))
    alice.add_event(Event("Lunch with Jack", time(13, 0), time(14, 0)))
    alice.add_event(Event("Yoga", time(16, 0), time(17, 0)))
    calendar.add_person(alice)

    jack = Person("Jack")
    jack.add_event(Event("Morning meeting", time(8, 0), time(8, 50)))
    jack.add_event(Event("Sales call", time(9, 0), time(9, 40)))
    jack.add_event(Event("Lunch with Alice", time(13, 0), time(14, 0)))
    jack.add_event(Event("Yoga", time(16, 0), time(17, 0)))
    calendar.add_person(jack)

    bob = Person("Bob")
    bob.add_event(Event("Morning meeting", time(8, 0), time(9, 30)))
    bob.add_event(Event("Morning meeting 2", time(9, 30), time(9, 40)))
    bob.add_event(Event("Q3 review", time(10, 0), time(11, 30)))
    bob.add_event(Event("Lunch and siesta", time(13, 0), time(15, 0)))
    bob.add_event(Event("Yoga", time(16, 0), time(17, 0)))
    calendar.add_person(bob)

    return calendar
