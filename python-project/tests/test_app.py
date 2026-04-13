"""
Unit tests for Comp calendar scheduler
"""

import pytest
from datetime import time, timedelta

from io_comp.models import Calendar, Person, Event
from io_comp.services import CalendarService
from io_comp.exceptions import PersonNotFoundError, InvalidDurationError, InvalidRequestError


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
def empty_calendar():
    """Fixture providing an empty calendar."""
    return Calendar()


@pytest.fixture
def example_calendar():
    """
    Fixture providing the example calendar from README:

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


class TestCalendarService:
    """Test suite for CalendarService."""

    def test_find_slots_alice_and_jack_60_minutes(self, example_calendar):
        """
        Test the README example:
        - Alice & Jack, 60-minute meeting
        - Expected slots: 07:00, 09:40, 14:00, 17:00
        """
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=60))

        expected_slots = [
            (time(7, 0),  time(8, 0)),
            (time(9, 40), time(13, 0)),
            (time(14, 0), time(16, 0)),
            (time(17, 0), time(19, 0)),
        ]
        assert slots == expected_slots

    def test_find_slots_single_person_no_conflicts(self, example_calendar):
        """
        Bob is busy 08:00-09:30, 09:30-09:40, 10:00-11:30, 13:00-15:00, 16:00-17:00.
        Free slots >= 60 min: 07:00, 11:30, 15:00, 17:00.
        """
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Bob"], timedelta(minutes=60))

        expected_slots = [
            (time(7, 0),   time(8, 0)),
            (time(11, 30), time(13, 0)),
            (time(15, 0),  time(16, 0)),
            (time(17, 0),  time(19, 0)),
        ]
        assert slots == expected_slots

    def test_no_available_slots(self, empty_calendar):
        """Person booked for the entire working day - no slots available."""
        person = Person("FullDay")
        person.add_event(Event("Busy", time(7, 0), time(19, 0)))
        empty_calendar.add_person(person)

        service = make_service(empty_calendar)
        slots = service.find_available_slots(["FullDay"], timedelta(minutes=60))

        assert slots == []

    def test_slots_with_short_duration(self, example_calendar):
        """With 15-minute duration, more slots are available including 07:00."""
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=15))

        assert any(start == time(7, 0) for start, _ in slots)

    def test_slots_with_long_duration(self, example_calendar):
        """With 4-hour duration, no slots fit for Alice & Jack."""
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Alice", "Jack"], timedelta(hours=4))

        assert len(slots) == 0

    def test_boundary_case_start_of_day(self, empty_calendar):
        """Person with no events - 07:00 should be available."""
        person = Person("Empty")
        empty_calendar.add_person(person)

        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Empty"], timedelta(minutes=60))

        assert any(start == time(7, 0) for start, _ in slots)

    def test_boundary_case_end_of_day(self, empty_calendar):
        """Person with no events - one continuous free interval 07:00-19:00."""
        person = Person("Empty")
        empty_calendar.add_person(person)

        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Empty"], timedelta(minutes=60))

        assert slots == [(time(7, 0), time(19, 0))]

    def test_overlapping_events_merge_correctly(self, empty_calendar):
        """Three overlapping events merge into one busy period 08:00-12:00."""
        person = Person("Overlap")
        person.add_event(Event("Event1", time(8, 0), time(10, 0)))
        person.add_event(Event("Event2", time(9, 0), time(11, 0)))
        person.add_event(Event("Event3", time(10, 30), time(12, 0)))
        empty_calendar.add_person(person)

        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Overlap"], timedelta(minutes=60))

        assert any(start == time(7, 0) for start, _ in slots)
        assert any(start == time(12, 0) for start, _ in slots)

    def test_adjacent_events_no_gap(self, empty_calendar):
        """Adjacent events 08:00-09:00 and 09:00-10:00 leave no gap between them."""
        person = Person("Adjacent")
        person.add_event(Event("Event1", time(8, 0), time(9, 0)))
        person.add_event(Event("Event2", time(9, 0), time(10, 0)))
        empty_calendar.add_person(person)

        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Adjacent"], timedelta(minutes=60))

        assert any(start == time(7, 0) for start, _ in slots)
        assert any(start == time(10, 0) for start, _ in slots)

    def test_error_empty_person_list(self, example_calendar):
        """Empty person list raises ValueError."""
        service = make_service(example_calendar)

        with pytest.raises(InvalidRequestError):
            service.find_available_slots([], timedelta(minutes=60))

    def test_error_person_not_found(self, example_calendar):
        """Non-existent person raises ValueError."""
        service = make_service(example_calendar)

        with pytest.raises(PersonNotFoundError):
            service.find_available_slots(["NonExistent"], timedelta(minutes=60))

    def test_error_zero_duration(self, example_calendar):
        """Zero duration raises ValueError."""
        service = make_service(example_calendar)

        with pytest.raises(InvalidDurationError):
            service.find_available_slots(["Alice"], timedelta(minutes=0))

    def test_error_duration_exceeds_working_day(self, example_calendar):
        """Duration exceeding 12-hour working day raises ValueError."""
        service = make_service(example_calendar)

        with pytest.raises(InvalidDurationError):
            service.find_available_slots(["Alice"], timedelta(hours=13))

    def test_multiple_people_complex_schedule(self, example_calendar):
        """
        All three people - Bob busy 13:00-15:00 blocks the 14:00 slot.
        Free slots >= 60 min: 07:00, 11:30, 15:00, 17:00.
        """
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Alice", "Jack", "Bob"], timedelta(minutes=60))

        expected = [
            (time(7, 0),   time(8, 0)),
            (time(11, 30), time(13, 0)),
            (time(15, 0),  time(16, 0)),
            (time(17, 0),  time(19, 0)),
        ]
        assert slots == expected
