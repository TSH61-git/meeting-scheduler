"""
CSV data loader for parsing calendar.csv files.
"""

import csv
from datetime import time
from pathlib import Path
from typing import Optional
import logging

from io_comp.models import Calendar, Person, Event


logger = logging.getLogger(__name__)


class CSVDataLoader:
    """
    Loads calendar data from a CSV file into a Calendar object.
    
    CSV Format:
        Person name, Event subject, Event start time, Event end time
        Example: Alice,"Morning meeting",08:00,09:30
    """

    def __init__(self, file_path: str):
        """
        Initialize the CSV data loader.
        
        Args:
            file_path: Path to the CSV file.
        """
        self.file_path = Path(file_path)

    def load(self) -> Calendar:
        """
        Load and parse the CSV file into a Calendar object.
        
        Returns:
            A populated Calendar object.
            
        Raises:
            FileNotFoundError: If the CSV file does not exist.
            ValueError: If CSV format is invalid or data cannot be parsed.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Calendar file not found: {self.file_path}")

        calendar = Calendar()
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                row_number = 0
                
                for row in reader:
                    row_number += 1
                    
                    # Skip empty rows
                    if not row or all(cell.strip() == '' for cell in row):
                        continue
                    
                    # Validate row format
                    if len(row) != 4:
                        raise ValueError(
                            f"Row {row_number}: Expected 4 columns, got {len(row)}. "
                            f"Format: Name, Subject, StartTime, EndTime"
                        )
                    
                    try:
                        name = row[0].strip()
                        subject = row[1].strip()
                        start_time_str = row[2].strip()
                        end_time_str = row[3].strip()
                        
                        # Validate fields
                        if not name:
                            raise ValueError(f"Row {row_number}: Person name is empty")
                        if not subject:
                            raise ValueError(f"Row {row_number}: Event subject is empty")
                        
                        # Parse times
                        start_time = self._parse_time(start_time_str, row_number, "start")
                        end_time = self._parse_time(end_time_str, row_number, "end")
                        
                        # Validate times are within working hours
                        self._validate_working_hours(start_time, row_number, "start")
                        self._validate_working_hours(end_time, row_number, "end")
                        
                        # Create or retrieve person
                        if name not in calendar.people:
                            person = Person(name)
                            calendar.add_person(person)
                        else:
                            person = calendar.get_person(name)
                        
                        # Create and add event
                        event = Event(subject, start_time, end_time)
                        person.add_event(event)
                        
                        logger.debug(
                            f"Loaded event: {name} - {subject} ({start_time}-{end_time})"
                        )
                        
                    except ValueError as e:
                        # Re-raise validation errors with context
                        raise ValueError(f"Row {row_number}: {str(e)}")
        
        except csv.Error as e:
            raise ValueError(f"CSV parsing error: {str(e)}")
        
        logger.info(f"Successfully loaded {calendar.person_count()} people with "
                    f"{len(calendar.get_all_events())} events")
        
        return calendar

    def _parse_time(self, time_str: str, row_number: int, field_name: str) -> time:
        """
        Parse a time string in HH:MM format.
        
        Args:
            time_str: Time string to parse (e.g., "09:30").
            row_number: Row number for error reporting.
            field_name: Name of the field ("start" or "end") for error messages.
            
        Returns:
            A datetime.time object.
            
        Raises:
            ValueError: If time format is invalid.
        """
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid {field_name} time format '{time_str}'. "
                    f"Expected HH:MM format"
                )
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            return time(hour, minute)
        
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid {field_name} time '{time_str}'. "
                f"Expected HH:MM format (e.g., 09:30). Details: {str(e)}"
            )

    def _validate_working_hours(self, event_time: time, row_number: int, field_name: str) -> None:
        """
        Validate that a time is within working hours (07:00-19:00).
        
        Args:
            event_time: The time to validate.
            row_number: Row number for error reporting.
            field_name: Name of the field ("start" or "end") for error messages.
            
        Raises:
            ValueError: If time is outside working hours.
        """
        working_start = time(7, 0)
        working_end = time(19, 0)
        
        if not (working_start <= event_time < working_end):
            raise ValueError(
                f"{field_name.capitalize()} time {event_time} is outside "
                f"working hours ({working_start}-{working_end})"
            )
