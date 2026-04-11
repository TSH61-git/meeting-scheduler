"""
Application configuration - single source of truth for working hours.
"""

from datetime import time
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkingHoursConfig:
    start: time = time(7, 0)
    end: time = time(19, 0)


DEFAULT_WORKING_HOURS = WorkingHoursConfig()
