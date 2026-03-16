"""
Calendar application entry point.
Finds available meeting slots for a group of people using the DI container.
"""

import sys
import logging
from datetime import timedelta
from pathlib import Path

from io_comp.di import DIContainer
from io_comp.di.container import create_default_container


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    try:
        csv_file_path = Path(__file__).parent.parent / "resources" / "calendar.csv"
        if not csv_file_path.exists():
            logger.error(f"Calendar file not found: {csv_file_path}")
            print(f"Error: Calendar file not found at {csv_file_path}")
            sys.exit(1)

        logger.info("Initializing application...")
        calendar_service = create_default_container(str(csv_file_path)).get("calendar_service")

        person_names, duration_minutes = _resolve_inputs()
        available_slots = calendar_service.find_available_slots(
            person_names, timedelta(minutes=duration_minutes)
        )
        display_results(person_names, duration_minutes, available_slots)

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(1)


def _resolve_inputs() -> tuple:
    """Return (person_names, duration_minutes) from CLI args or interactive prompt."""
    if len(sys.argv) > 1:
        return parse_args(sys.argv[1:])
    return prompt_user()


def parse_args(args: list) -> tuple:
    """
    Parse command-line arguments.
    Format: name1 name2 ... duration_in_minutes
    
    Args:
        args: Remaining command-line arguments after script name.
        
    Returns:
        Tuple of (person_names_list, duration_minutes).
        
    Raises:
        ValueError: If arguments are invalid.
    """
    if len(args) < 2:
        raise ValueError(
            "Usage: python -m io_comp.app [person1] [person2] ... [duration_minutes]\n"
            "Example: python -m io_comp.app Alice Jack 60"
        )
    
    try:
        duration_minutes = int(args[-1])
        person_names = args[:-1]
        
        if not person_names:
            raise ValueError("At least one person name is required")
        
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        
        return person_names, duration_minutes
    
    except ValueError as e:
        raise ValueError(
            f"Invalid arguments: {e}\n"
            f"Usage: python -m io_comp.app [person1] [person2] ... [duration_minutes]\n"
            f"Example: python -m io_comp.app Alice Jack 60"
        )


def prompt_user() -> tuple:
    """
    Prompt the user interactively for person names and meeting duration.
    
    Returns:
        Tuple of (person_names_list, duration_minutes).
        
    Raises:
        ValueError: If user input is invalid.
    """
    print("\n=== Calendar Available Slots Finder ===\n")
    
    # Get person names
    while True:
        names_input = input("Enter person names (comma-separated): ").strip()
        if names_input:
            person_names = [name.strip() for name in names_input.split(",")]
            person_names = [n for n in person_names if n]  # Remove empty strings
            if person_names:
                break
        print("Please enter at least one name.")
    
    # Get meeting duration
    while True:
        duration_input = input("Enter meeting duration in minutes: ").strip()
        try:
            duration_minutes = int(duration_input)
            if duration_minutes > 0:
                break
            print("Duration must be positive.")
        except ValueError:
            print("Please enter a valid number.")
    
    return person_names, duration_minutes


def display_results(person_names: list, duration_minutes: int, available_slots: list):
    """
    Display the search results in a user-friendly format.
    
    Args:
        person_names: List of person names.
        duration_minutes: Meeting duration in minutes.
        available_slots: List of (start_time, end_time) tuples representing available time ranges.
    """
    print(f"\n=== Available Meeting Slots ===")
    print(f"People: {', '.join(person_names)}")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Working hours: 07:00 - 19:00\n")
    
    if not available_slots:
        print("No available slots found for all participants.")
        return
    
    for start_time, end_time in available_slots:
        start_str = start_time.strftime("%H:%M")
        
        # Calculate latest possible start time (end_time - duration)
        end_minutes_total = end_time.hour * 60 + end_time.minute
        latest_start_minutes = end_minutes_total - duration_minutes
        latest_start_hour = latest_start_minutes // 60
        latest_start_minute = latest_start_minutes % 60
        latest_start_str = f"{latest_start_hour:02d}:{latest_start_minute:02d}"
        
        # If start and end are the same, show only start time
        if start_str == latest_start_str:
            print(f"Starting Time of available slots: {start_str}")
        else:
            print(f"Starting Time of available slots: {start_str} - {latest_start_str}")
    
    print(f"\nTotal: {len(available_slots)} available slot(s)")


if __name__ == "__main__":
    main()
