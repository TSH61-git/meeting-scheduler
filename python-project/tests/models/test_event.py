"""
Tests for the Event model.
"""

import pytest
from datetime import time
from dataclasses import FrozenInstanceError

from io_comp.models import Event
from io_comp.exceptions import InvalidEventError


class TestEvent:

    def test_valid_event_creation(self):
        """Event is created successfully with valid times."""
        event = Event("Meeting", time(8, 0), time(9, 0))
        assert event.subject == "Meeting"
        assert event.start_time == time(8, 0)
        assert event.end_time == time(9, 0)

    def test_end_before_start_raises(self):
        """Event with end_time before start_time raises InvalidEventError."""
        with pytest.raises(InvalidEventError):
            Event("Bad", time(10, 0), time(9, 0))

    def test_end_equal_start_raises(self):
        """Event with end_time equal to start_time raises InvalidEventError."""
        with pytest.raises(InvalidEventError):
            Event("Bad", time(10, 0), time(10, 0))

    def test_immutable_subject(self):
        """Event fields cannot be modified after creation (frozen dataclass)."""
        event = Event("Meeting", time(8, 0), time(9, 0))
        with pytest.raises(FrozenInstanceError):
            event.subject = "Changed"

    def test_immutable_start_time(self):
        """start_time cannot be modified after creation."""
        event = Event("Meeting", time(8, 0), time(9, 0))
        with pytest.raises(FrozenInstanceError):
            event.start_time = time(10, 0)

    def test_immutable_end_time(self):
        """end_time cannot be modified after creation."""
        event = Event("Meeting", time(8, 0), time(9, 0))
        with pytest.raises(FrozenInstanceError):
            event.end_time = time(11, 0)

    def test_duration_minutes(self):
        """duration_minutes returns correct duration."""
        event = Event("Meeting", time(8, 0), time(9, 30))
        assert event.duration_minutes() == 90

    def test_overlaps_with_true(self):
        """Two overlapping events return True."""
        e1 = Event("E1", time(8, 0), time(10, 0))
        e2 = Event("E2", time(9, 0), time(11, 0))
        assert e1.overlaps_with(e2)
        assert e2.overlaps_with(e1)

    def test_overlaps_with_false(self):
        """Two non-overlapping events return False."""
        e1 = Event("E1", time(8, 0), time(9, 0))
        e2 = Event("E2", time(10, 0), time(11, 0))
        assert not e1.overlaps_with(e2)

    def test_adjacent_events_do_not_overlap(self):
        """Adjacent events (end == start) do not overlap."""
        e1 = Event("E1", time(8, 0), time(9, 0))
        e2 = Event("E2", time(9, 0), time(10, 0))
        assert not e1.overlaps_with(e2)

    def test_equality(self):
        """Two events with same fields are equal."""
        e1 = Event("Meeting", time(8, 0), time(9, 0))
        e2 = Event("Meeting", time(8, 0), time(9, 0))
        assert e1 == e2

    def test_inequality(self):
        """Two events with different fields are not equal."""
        e1 = Event("Meeting", time(8, 0), time(9, 0))
        e2 = Event("Meeting", time(8, 0), time(10, 0))
        assert e1 != e2
