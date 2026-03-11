"""
Unit tests for Comp calendar scheduler
"""

import pytest
from datetime import time, timedelta

from io_comp.models import Calendar, Person, Event
from io_comp.services import CalendarService


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
    
    # Alice's events
    alice = Person("Alice")
    alice.add_event(Event("Morning meeting", time(8, 0), time(9, 30)))
    alice.add_event(Event("Lunch with Jack", time(13, 0), time(14, 0)))
    alice.add_event(Event("Yoga", time(16, 0), time(17, 0)))
    calendar.add_person(alice)
    
    # Jack's events
    jack = Person("Jack")
    jack.add_event(Event("Morning meeting", time(8, 0), time(8, 50)))
    jack.add_event(Event("Sales call", time(9, 0), time(9, 40)))
    jack.add_event(Event("Lunch with Alice", time(13, 0), time(14, 0)))
    jack.add_event(Event("Yoga", time(16, 0), time(17, 0)))
    calendar.add_person(jack)
    
    # Bob's events
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
        - Alice & Jack
        - 60-minute meeting
        - Expected slots: 07:00, 09:40, 14:00, 17:00
        """
        service = CalendarService(example_calendar)
        slots = service.find_available_slots(["Alice", "Jack"], timedelta(minutes=60))
        
        # Convert to list of time objects for comparison
        expected_slots = [
            time(7, 0),    # Before any events
            time(9, 40),   # After Jack's sales call (09:00-09:40)
            time(14, 0),   # After lunch
            time(17, 0),   # After yoga
        ]
        
        assert slots == expected_slots, (
            f"Expected {expected_slots}, got {slots}"
        )

    def test_find_slots_single_person_no_conflicts(self, example_calendar):
        """
        Test finding slots for a single person:
        - Should return all free time slots in working hours (07:00-19:00)
        - Bob is busy 08:00-09:30, 09:30-09:40, 10:00-11:30, 13:00-15:00, 16:00-17:00
        """
        service = CalendarService(example_calendar)
        slots = service.find_available_slots(["Bob"], timedelta(minutes=60))
        
        # Bob's free slots (60+ minutes):
        # 07:00-08:00 (1 hour) ✓
        # 09:40-10:00 (20 min) ✗
        # 11:30-13:00 (90 min) ✓
        # 15:00-16:00 (1 hour) ✓
        # 17:00-19:00 (2 hours) ✓
        expected_slots = [
            time(7, 0),
            time(11, 30),
            time(15, 0),
            time(17, 0),
        ]
        
        assert slots == expected_slots

    def test_no_available_slots(self, empty_calendar):
        """
        Test scenario where no slots are available:
        - Person with calendar full all day
        """
        person = Person("FullDay")
        # Book entire working day
        person.add_event(Event("Busy", time(7, 0), time(19, 0)))
        empty_calendar.add_person(person)
        
        service = CalendarService(empty_calendar)
        slots = service.find_available_slots(["FullDay"], timedelta(minutes=60))
        
        assert slots == []

    def test_slots_with_short_duration(self, example_calendar):
        """
        Test finding slots with a very short duration (15 minutes):
        Many more slots should be available.
        """
        service = CalendarService(example_calendar)
        slots = service.find_available_slots(
            ["Alice", "Jack"],
            timedelta(minutes=15)
        )
        
        # With 15-minute duration, many small gaps become available
        # At minimum: 07:00 should be available
        assert time(7, 0) in slots

    def test_slots_with_long_duration(self, example_calendar):
        """
        Test finding slots with a very long duration (4 hours):
        Few or no slots should fit.
        """
        service = CalendarService(example_calendar)
        slots = service.find_available_slots(
            ["Alice", "Jack"],
            timedelta(hours=4)
        )
        
        # Most gaps are < 4 hours, so expect empty or very few
        assert len(slots) <= 1

    def test_boundary_case_start_of_day(self, empty_calendar):
        """
        Test that 07:00 (start of working hours) is always available
        if the person has no events.
        """
        person = Person("Empty")
        # No events
        empty_calendar.add_person(person)
        
        service = CalendarService(empty_calendar)
        slots = service.find_available_slots(["Empty"], timedelta(minutes=60))
        
        # Should have one slot at 07:00
        assert time(7, 0) in slots

    def test_boundary_case_end_of_day(self, empty_calendar):
        """
        Test slots near end of working hours:
        - With no events, the entire day (07:00-19:00) is one free interval
        - We return the start of free intervals, so just 07:00
        - (A meeting could start anywhere from 07:00-18:00, but we return interval starts)
        """
        person = Person("Empty")
        empty_calendar.add_person(person)
        
        service = CalendarService(empty_calendar)
        slots = service.find_available_slots(["Empty"], timedelta(minutes=60))
        
        # One continuous free interval: 07:00-19:00
        assert slots == [time(7, 0)]

    def test_overlapping_events_merge_correctly(self, empty_calendar):
        """
        Test that overlapping events are merged correctly:
        - Three overlapping events should merge into one continuous busy period
        """
        person = Person("Overlap")
        person.add_event(Event("Event1", time(8, 0), time(10, 0)))
        person.add_event(Event("Event2", time(9, 0), time(11, 0)))  # Overlaps
        person.add_event(Event("Event3", time(10, 30), time(12, 0)))  # Overlaps
        empty_calendar.add_person(person)
        
        service = CalendarService(empty_calendar)
        slots = service.find_available_slots(["Overlap"], timedelta(minutes=60))
        
        # Should have slots in the gaps:
        # 07:00-08:00 (1 hour) ✓
        # 12:00-19:00 (7 hours) ✓
        assert time(7, 0) in slots
        assert time(12, 0) in slots

    def test_adjacent_events_no_gap(self, empty_calendar):
        """
        Test that adjacent events (no gap between them) are handled:
        - Event1: 08:00-09:00
        - Event2: 09:00-10:00
        - No free slot between them
        """
        person = Person("Adjacent")
        person.add_event(Event("Event1", time(8, 0), time(9, 0)))
        person.add_event(Event("Event2", time(9, 0), time(10, 0)))
        empty_calendar.add_person(person)
        
        service = CalendarService(empty_calendar)
        slots = service.find_available_slots(["Adjacent"], timedelta(minutes=60))
        
        # Should have slots:
        # 07:00-08:00 (1 hour) ✓
        # 10:00-19:00 (9 hours) ✓
        assert time(7, 0) in slots
        assert time(10, 0) in slots

    def test_error_empty_person_list(self, example_calendar):
        """Test that empty person list raises ValueError."""
        service = CalendarService(example_calendar)
        
        with pytest.raises(ValueError, match="At least one person"):
            service.find_available_slots([], timedelta(minutes=60))

    def test_error_person_not_found(self, example_calendar):
        """Test that requesting a non-existent person raises ValueError."""
        service = CalendarService(example_calendar)
        
        with pytest.raises(ValueError, match="not found"):
            service.find_available_slots(["NonExistent"], timedelta(minutes=60))

    def test_error_zero_duration(self, example_calendar):
        """Test that zero or negative duration raises ValueError."""
        service = CalendarService(example_calendar)
        
        with pytest.raises(ValueError, match="positive"):
            service.find_available_slots(["Alice"], timedelta(minutes=0))

    def test_error_duration_exceeds_working_day(self, example_calendar):
        """Test that duration exceeding the working day raises ValueError."""
        service = CalendarService(example_calendar)
        
        # Working day is 12 hours (07:00-19:00)
        with pytest.raises(ValueError, match="exceeds working day"):
            service.find_available_slots(["Alice"], timedelta(hours=13))

    def test_multiple_people_complex_schedule(self, example_calendar):
        """
        Test with all three people to ensure complex merging works:
        - Alice, Jack, and Bob all busy at different times
        - Bob busy 13:00-15:00, so slots at 14:00 don't work (overlaps Bob's lunch)
        """
        service = CalendarService(example_calendar)
        slots = service.find_available_slots(
            ["Alice", "Jack", "Bob"],
            timedelta(minutes=60)
        )

        # Merged busy: 08:00-09:40, 10:00-11:30, 13:00-15:00, 16:00-17:00
        # Free: 07:00-08:00, 11:30-13:00, 15:00-16:00, 17:00-19:00
        expected = [
            time(7, 0),
            time(11, 30),
            time(15, 0),    # Not 14:00, because Bob is busy 13:00-15:00
            time(17, 0),
        ]
        
        assert slots == expected
