"""
Tests for CalendarService.
"""

import pytest
from datetime import time, timedelta

from io_comp.models import Calendar, Person, Event
from io_comp.services import CalendarService
from io_comp.exceptions import PersonNotFoundError, InvalidDurationError, InvalidRequestError
from tests.conftest import make_service


class TestCalendarService:

    def test_readme_example_alice_and_jack(self, example_calendar):
        """README example: Alice & Jack, 60 min → 4 slots."""
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=60))
        assert slots == [
            (time(7, 0),  time(8, 0)),
            (time(9, 40), time(13, 0)),
            (time(14, 0), time(16, 0)),
            (time(17, 0), time(19, 0)),
        ]

    def test_single_person_with_events(self, example_calendar):
        """Bob's free slots >= 60 min: 07:00, 11:30, 15:00, 17:00."""
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Bob"], timedelta(minutes=60))
        assert slots == [
            (time(7, 0),   time(8, 0)),
            (time(11, 30), time(13, 0)),
            (time(15, 0),  time(16, 0)),
            (time(17, 0),  time(19, 0)),
        ]

    def test_person_with_no_events(self, empty_calendar):
        """Person with no events - entire day is free."""
        empty_calendar.add_person(Person("Free"))
        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Free"], timedelta(minutes=60))
        assert slots == [(time(7, 0), time(19, 0))]

    def test_no_available_slots_full_day(self, empty_calendar):
        """Person booked all day - no slots."""
        person = Person("FullDay")
        person.add_event(Event("Busy", time(7, 0), time(19, 0)))
        empty_calendar.add_person(person)
        service = make_service(empty_calendar)
        assert service.find_available_slots(["FullDay"], timedelta(minutes=60)) == []

    def test_duration_exactly_fits_slot(self, empty_calendar):
        """Duration exactly equal to free slot - slot is included."""
        person = Person("Alice")
        person.add_event(Event("Morning", time(7, 0), time(8, 0)))
        person.add_event(Event("Afternoon", time(9, 0), time(19, 0)))
        empty_calendar.add_person(person)
        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Alice"], timedelta(minutes=60))
        assert slots == [(time(8, 0), time(9, 0))]

    def test_duration_too_long_for_slot(self, empty_calendar):
        """Duration longer than free slot - slot is excluded."""
        person = Person("Alice")
        person.add_event(Event("Morning", time(7, 0), time(8, 0)))
        person.add_event(Event("Afternoon", time(9, 0), time(19, 0)))
        empty_calendar.add_person(person)
        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Alice"], timedelta(minutes=90))
        assert slots == []

    def test_overlapping_events_merged(self, empty_calendar):
        """Overlapping events merge into one busy period."""
        person = Person("Alice")
        person.add_event(Event("E1", time(8, 0), time(10, 0)))
        person.add_event(Event("E2", time(9, 0), time(11, 0)))
        person.add_event(Event("E3", time(10, 30), time(12, 0)))
        empty_calendar.add_person(person)
        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Alice"], timedelta(minutes=60))
        assert any(start == time(7, 0) for start, _ in slots)
        assert any(start == time(12, 0) for start, _ in slots)
        assert not any(start == time(8, 0) for start, _ in slots)

    def test_adjacent_events_no_gap(self, empty_calendar):
        """Adjacent events leave no gap between them."""
        person = Person("Alice")
        person.add_event(Event("E1", time(8, 0), time(9, 0)))
        person.add_event(Event("E2", time(9, 0), time(10, 0)))
        empty_calendar.add_person(person)
        service = make_service(empty_calendar)
        slots = service.find_available_slots(["Alice"], timedelta(minutes=60))
        assert any(start == time(7, 0) for start, _ in slots)
        assert any(start == time(10, 0) for start, _ in slots)
        assert not any(start == time(9, 0) for start, _ in slots)

    def test_short_duration_more_slots(self, example_calendar):
        """15-minute duration yields more slots than 60-minute."""
        service = make_service(example_calendar)
        slots_60 = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=60))
        slots_15 = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=15))
        assert len(slots_15) >= len(slots_60)

    def test_long_duration_no_slots(self, example_calendar):
        """4-hour duration yields no slots for Alice & Jack."""
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Alice", "Jack"], timedelta(hours=4))
        assert slots == []

    def test_three_people_complex_schedule(self, example_calendar):
        """All three people - Bob blocks 14:00 slot."""
        service = make_service(example_calendar)
        slots = service.find_available_slots(["Alice", "Jack", "Bob"], timedelta(minutes=60))
        assert slots == [
            (time(7, 0),   time(8, 0)),
            (time(11, 30), time(13, 0)),
            (time(15, 0),  time(16, 0)),
            (time(17, 0),  time(19, 0)),
        ]

    def test_error_empty_person_list(self, example_calendar):
        """Empty person list raises InvalidRequestError."""
        service = make_service(example_calendar)
        with pytest.raises(InvalidRequestError):
            service.find_available_slots([], timedelta(minutes=60))

    def test_error_person_not_found(self, example_calendar):
        """Non-existent person raises PersonNotFoundError."""
        service = make_service(example_calendar)
        with pytest.raises(PersonNotFoundError):
            service.find_available_slots(["NonExistent"], timedelta(minutes=60))

    def test_error_zero_duration(self, example_calendar):
        """Zero duration raises InvalidDurationError."""
        service = make_service(example_calendar)
        with pytest.raises(InvalidDurationError):
            service.find_available_slots(["Alice"], timedelta(minutes=0))

    def test_error_negative_duration(self, example_calendar):
        """Negative duration raises InvalidDurationError."""
        service = make_service(example_calendar)
        with pytest.raises(InvalidDurationError):
            service.find_available_slots(["Alice"], timedelta(minutes=-30))

    def test_error_duration_exceeds_working_day(self, example_calendar):
        """Duration exceeding 12-hour working day raises InvalidDurationError."""
        service = make_service(example_calendar)
        with pytest.raises(InvalidDurationError):
            service.find_available_slots(["Alice"], timedelta(hours=13))
