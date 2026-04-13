"""
CSV implementation of CalendarRepository.
"""

import csv
from datetime import time
from pathlib import Path
import logging

from io_comp.models import Calendar, Person, Event
from io_comp.config import DEFAULT_WORKING_HOURS
from io_comp.exceptions import CsvParseError


logger = logging.getLogger(__name__)


class CSVCalendarRepository:
    """
    Loads calendar data from a CSV file into a Calendar object.
    
    CSV Format:
        Person name, Event subject, Event start time, Event end time
        Example: Alice,"Morning meeting",08:00,09:30

    Implements CalendarRepository Protocol.
    """

    def __init__(self, file_path: str) -> None:
        """Initialize with path to the CSV file."""
        self.file_path = Path(file_path)

    def load(self) -> Calendar:
        """Load and parse the CSV file into a Calendar object."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Calendar file not found: {self.file_path}")

        calendar = Calendar()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                for row_number, row in enumerate(csv.reader(csvfile), start=1):
                    if not row or all(cell.strip() == '' for cell in row):
                        continue
                    self._process_row(row, row_number, calendar)
        except csv.Error as e:
            raise CsvParseError(f"CSV parsing error: {e}")

        logger.info(f"Successfully loaded {calendar.person_count()} people with "
                    f"{len(calendar.get_all_events())} events")
        return calendar

    def _process_row(self, row: list, row_number: int, calendar: Calendar) -> None:
        """Parse and validate a single CSV row, then add the event to the calendar."""
        if len(row) != 4:
            raise CsvParseError(
                f"Row {row_number}: Expected 4 columns, got {len(row)}. "
                f"Format: Name, Subject, StartTime, EndTime"
            )
        try:
            name, subject, start_str, end_str = (cell.strip() for cell in row)

            if not name:
                raise CsvParseError("Person name is empty")
            if not subject:
                raise CsvParseError("Event subject is empty")

            start_time = self._parse_time(start_str, row_number, "start")
            end_time = self._parse_time(end_str, row_number, "end")
            self._validate_working_hours(start_time, "start")
            self._validate_working_hours(end_time, "end")

            if calendar.get_person(name) is None:
                calendar.add_person(Person(name))
            calendar.get_person(name).add_event(Event(subject, start_time, end_time))

            logger.debug(f"Loaded event: {name} - {subject} ({start_time}-{end_time})")
        except CsvParseError as e:
            raise CsvParseError(f"Row {row_number}: {e}")

    def _parse_time(self, time_str: str, row_number: int, field_name: str) -> time:
        """Parse HH:MM time string. Raises CsvParseError if format is invalid."""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError(f"Expected HH:MM format")
            return time(int(parts[0]), int(parts[1]))
        except (ValueError, TypeError) as e:
            raise CsvParseError(
                f"Invalid {field_name} time '{time_str}'. Expected HH:MM (e.g. 09:30). Details: {e}"
            )

    def _validate_working_hours(self, event_time: time, field_name: str) -> None:
        """Validate that a time is within working hours."""
        if not (DEFAULT_WORKING_HOURS.start <= event_time <= DEFAULT_WORKING_HOURS.end):
            raise CsvParseError(
                f"{field_name.capitalize()} time {event_time} is outside "
                f"working hours ({DEFAULT_WORKING_HOURS.start}-{DEFAULT_WORKING_HOURS.end})"
            )
