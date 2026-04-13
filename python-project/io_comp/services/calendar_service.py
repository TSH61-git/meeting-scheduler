"""
Calendar service with business logic for finding available meeting slots.
"""

from datetime import time, timedelta
from typing import List, Tuple
import logging

from io_comp.data import CalendarRepository
from io_comp.config import WorkingHoursConfig, DEFAULT_WORKING_HOURS
from io_comp.exceptions import PersonNotFoundError, InvalidDurationError, InvalidRequestError


logger = logging.getLogger(__name__)


class CalendarService:
    """
    Service class for calendar operations.
    
    Provides methods to find available meeting slots for a group of people
    using efficient interval merging algorithm.
    """

    def __init__(self, repo: CalendarRepository, config: WorkingHoursConfig = DEFAULT_WORKING_HOURS):
        """Initialize CalendarService with a repository and optional working hours config."""
        self.calendar = repo.load()
        self._config = config

    def find_available_slots(
        self,
        person_names: List[str],
        event_duration: timedelta
    ) -> List[Tuple[time, time]]:
        """Find all available time slots when all specified people are free, as (start, end) tuples."""
        self._validate_inputs(person_names, event_duration)

        combined_busy = self._merge_busy_intervals(*self._collect_busy_intervals(person_names))
        logger.debug(f"Combined busy intervals: {combined_busy}")

        free_intervals = self._get_free_intervals(combined_busy)
        logger.debug(f"Free intervals: {free_intervals}")

        available_slots = self._filter_slots_by_duration(free_intervals, event_duration)
        logger.info(f"Found {len(available_slots)} available slots for {len(person_names)} people")
        return available_slots

    def _collect_busy_intervals(self, person_names: List[str]) -> List[List[Tuple[time, time]]]:
        """Return a list of busy interval lists, one per person."""
        result = []
        for name in person_names:
            person = self.calendar.get_person(name)
            if person is None:
                raise PersonNotFoundError(f"Person '{name}' not found in calendar")
            busy = self._get_busy_intervals(person.events)
            logger.debug(f"{name}: {len(busy)} busy intervals")
            result.append(busy)
        return result

    def _validate_inputs(self, person_names: List[str], event_duration: timedelta) -> None:
        """Validate person list and event duration."""
        if not person_names or not isinstance(person_names, list):
            raise InvalidRequestError("At least one person must be specified")
        if event_duration.total_seconds() <= 0:
            raise InvalidDurationError("Event duration must be positive")
        working_day_minutes = self._time_difference_minutes(
            self._config.start, self._config.end
        )
        if event_duration.total_seconds() > working_day_minutes * 60:
            raise InvalidDurationError(
                f"Event duration ({event_duration}) exceeds working day length "
                f"({working_day_minutes} minutes)"
            )

    def _get_busy_intervals(self, events) -> List[Tuple[time, time]]:
        """Convert events to sorted (start, end) tuples."""
        return sorted((event.start_time, event.end_time) for event in events)

    def _merge_busy_intervals(self, *all_intervals) -> List[Tuple[time, time]]:
        """Flatten and merge overlapping intervals from multiple people into one sorted list."""
        flat = sorted(
            interval for intervals in all_intervals for interval in intervals
        )
        if not flat:
            return []

        merged = []
        current_start, current_end = flat[0]
        for start, end in flat[1:]:
            if start <= current_end:
                current_end = max(current_end, end)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = start, end
        merged.append((current_start, current_end))
        return merged

    def _get_free_intervals(self, busy_intervals: List[Tuple[time, time]]) -> List[Tuple[time, time]]:
        """Return free intervals within working hours given merged busy intervals."""
        free, current = [], self._config.start
        for busy_start, busy_end in busy_intervals:
            if current < busy_start:
                free.append((current, busy_start))
            current = max(current, busy_end)
        if current < self._config.end:
            free.append((current, self._config.end))
        return free

    def _filter_slots_by_duration(
        self,
        free_intervals: List[Tuple[time, time]],
        event_duration: timedelta
    ) -> List[Tuple[time, time]]:
        """Return only free intervals long enough to fit the event duration."""
        duration_minutes = int(event_duration.total_seconds() / 60)
        return [
            (start, end) for start, end in free_intervals
            if self._time_difference_minutes(start, end) >= duration_minutes
        ]

    def _time_difference_minutes(self, start: time, end: time) -> int:
        """Return the difference between two times in minutes."""
        return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
