"""
Calendar service with business logic for finding available meeting slots.
"""

from datetime import time, timedelta
from typing import List, Tuple
import logging

from io_comp.models import Calendar


logger = logging.getLogger(__name__)


class CalendarService:
    """
    Service class for calendar operations.
    
    Provides methods to find available meeting slots for a group of people
    using efficient interval merging algorithm.
    """

    # Define working hours as class constants
    WORKING_HOURS_START = time(7, 0)
    WORKING_HOURS_END = time(19, 0)

    def __init__(self, calendar: Calendar):
        """
        Initialize the CalendarService with a calendar.
        
        Args:
            calendar: A Calendar object containing people and their events.
        """
        self.calendar = calendar

    def find_available_slots(
        self,
        person_names: List[str],
        event_duration: timedelta
    ) -> List[time]:
        """
        Find all available time slots in a single day when all specified people
        are free, and the slot can accommodate the event duration.
        
        Algorithm:
        1. Validate inputs
        2. Get busy intervals for each person
        3. Merge busy intervals (interval merging)
        4. Find free intervals within working hours
        5. Filter by event duration and return start times
        
        Args:
            person_names: List of people who should attend the meeting.
            event_duration: Desired meeting duration as a timedelta.
            
        Returns:
            List of datetime.time objects representing available slot start times,
            sorted in chronological order. Empty list if no slots found.
            
        Raises:
            ValueError: If person names are invalid, duration is negative/zero,
                       or if no valid slots exist within working hours.
        """
        # Validate inputs
        self._validate_inputs(person_names, event_duration)
        
        # Get busy intervals for each person
        busy_intervals_per_person = []
        for name in person_names:
            person = self.calendar.get_person(name)
            if person is None:
                raise ValueError(f"Person '{name}' not found in calendar")
            
            busy = self._get_busy_intervals(person.events)
            busy_intervals_per_person.append(busy)
            logger.debug(f"{name}: {len(busy)} busy intervals")
        
        # Merge all busy intervals (union of all people's busy times)
        combined_busy = self._merge_busy_intervals(*busy_intervals_per_person)
        logger.debug(f"Combined busy intervals: {combined_busy}")
        
        # Get free intervals from combined busy intervals
        free_intervals = self._get_free_intervals(combined_busy)
        logger.debug(f"Free intervals: {free_intervals}")
        
        # Extract start times that fit the event duration
        available_slots = self._filter_slots_by_duration(free_intervals, event_duration)
        logger.info(f"Found {len(available_slots)} available slots for {len(person_names)} people")
        
        return available_slots

    def _validate_inputs(self, person_names: List[str], event_duration: timedelta) -> None:
        """
        Validate that inputs are valid.
        
        Args:
            person_names: List of person names.
            event_duration: Meeting duration.
            
        Raises:
            ValueError: If inputs are invalid.
        """
        if not person_names:
            raise ValueError("At least one person must be specified")
        
        if not isinstance(person_names, list):
            raise ValueError("person_names must be a list")
        
        if event_duration.total_seconds() <= 0:
            raise ValueError("Event duration must be positive")
        
        # Check that duration doesn't exceed the working day
        working_day_minutes = (
            (self.WORKING_HOURS_END.hour * 60 + self.WORKING_HOURS_END.minute) -
            (self.WORKING_HOURS_START.hour * 60 + self.WORKING_HOURS_START.minute)
        )
        if event_duration.total_seconds() > working_day_minutes * 60:
            raise ValueError(
                f"Event duration ({event_duration}) exceeds working day length "
                f"({working_day_minutes} minutes)"
            )

    def _get_busy_intervals(self, events) -> List[Tuple[time, time]]:
        """
        Convert a list of events into sorted busy time intervals.
        
        Args:
            events: List of Event objects.
            
        Returns:
            List of (start_time, end_time) tuples, sorted by start time.
        """
        intervals = [(event.start_time, event.end_time) for event in events]
        return sorted(intervals)

    def _merge_busy_intervals(self, *all_intervals) -> List[Tuple[time, time]]:
        """
        Merge multiple lists of busy intervals into a single sorted, non-overlapping list.
        
        This implements the interval merging algorithm:
        1. Collect all intervals from all people
        2. Sort by start time
        3. Iterate and merge overlapping/adjacent intervals
        
        Args:
            *all_intervals: Variable number of lists of (start, end) tuples.
            
        Returns:
            A single sorted list of non-overlapping (start, end) tuples.
        """
        # Flatten all intervals from all people
        flat_intervals = []
        for intervals in all_intervals:
            flat_intervals.extend(intervals)
        
        if not flat_intervals:
            return []
        
        # Sort by start time
        flat_intervals.sort(key=lambda x: x[0])
        
        # Merge overlapping intervals
        merged = []
        current_start, current_end = flat_intervals[0]
        
        for start, end in flat_intervals[1:]:
            if start <= current_end:
                # Overlapping or adjacent: extend current interval
                current_end = max(current_end, end)
            else:
                # No overlap: save current and start new
                merged.append((current_start, current_end))
                current_start, current_end = start, end
        
        # Don't forget the last interval
        merged.append((current_start, current_end))
        
        return merged

    def _get_free_intervals(self, busy_intervals: List[Tuple[time, time]]) -> List[Tuple[time, time]]:
        """
        Compute free time intervals from busy intervals within working hours.
        
        Args:
            busy_intervals: List of (start, end) time tuples representing busy times.
            
        Returns:
            List of (start, end) tuples representing free time slots.
        """
        free_intervals = []
        current_time = self.WORKING_HOURS_START
        
        for busy_start, busy_end in busy_intervals:
            # Add free interval before this busy period
            if current_time < busy_start:
                free_intervals.append((current_time, busy_start))
            
            # Move current time past this busy period
            current_time = max(current_time, busy_end)
        
        # Add final free interval until end of working hours
        if current_time < self.WORKING_HOURS_END:
            free_intervals.append((current_time, self.WORKING_HOURS_END))
        
        return free_intervals

    def _filter_slots_by_duration(
        self,
        free_intervals: List[Tuple[time, time]],
        event_duration: timedelta
    ) -> List[time]:
        """
        Extract slot start times from free intervals that can fit the event duration.
        
        Args:
            free_intervals: List of (start, end) time tuples.
            event_duration: Required meeting duration as a timedelta.
            
        Returns:
            List of datetime.time objects representing valid slot start times.
        """
        available_slots = []
        duration_minutes = int(event_duration.total_seconds() / 60)
        
        for start, end in free_intervals:
            # Check if this interval can fit the event
            interval_minutes = self._time_difference_minutes(start, end)
            if interval_minutes >= duration_minutes:
                available_slots.append(start)
                logger.debug(
                    f"Valid slot: {start} - {end} ({interval_minutes} min)"
                )
        
        return available_slots

    def _time_difference_minutes(self, start: time, end: time) -> int:
        """
        Calculate the difference between two times in minutes.
        
        Args:
            start: Start time.
            end: End time.
            
        Returns:
            Difference in minutes (assumes end > start, same day).
        """
        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute
        return end_minutes - start_minutes
