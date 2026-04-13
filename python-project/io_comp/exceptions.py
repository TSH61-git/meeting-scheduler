"""
Domain-specific exceptions for the calendar application.
"""


class CalendarError(Exception):
    """Base exception for all calendar domain errors."""


class PersonNotFoundError(CalendarError):
    """Raised when a requested person does not exist in the calendar."""


class InvalidDurationError(CalendarError):
    """Raised when a meeting duration is invalid (zero, negative, or exceeds working day)."""


class InvalidRequestError(CalendarError):
    """Raised when a request is malformed (e.g. empty person list)."""


class InvalidEventError(CalendarError):
    """Raised when an event has invalid time boundaries (end <= start)."""


class CsvParseError(CalendarError):
    """Raised when the CSV file cannot be parsed due to format or data errors."""
