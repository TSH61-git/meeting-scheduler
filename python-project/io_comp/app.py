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
    """
    Main entry point for the calendar application.
    
    Usage:
        python -m io_comp.app
        -> Prompts for person names and meeting duration
        
    Or call with arguments:
        python -m io_comp.app Alice Jack 60
        -> Finds 60-minute slots for Alice and Jack
    """
    try:
        # Determine CSV file path (relative to this module)
        module_dir = Path(__file__).parent.parent
        csv_file_path = module_dir / "resources" / "calendar.csv"
        
        if not csv_file_path.exists():
            logger.error(f"Calendar file not found: {csv_file_path}")
            print(f"Error: Calendar file not found at {csv_file_path}")
            sys.exit(1)
        
        # Initialize DI container with calendar data
        logger.info("Initializing application...")
        container = create_default_container(str(csv_file_path))
        
        # Get the calendar service from the container
        calendar_service = container.get("calendar_service")
        
        # Parse command-line arguments or prompt user
        if len(sys.argv) > 1:
            # Arguments provided: calendar.py Alice Jack 60
            person_names, duration_minutes = parse_args(sys.argv[1:])
        else:
            # Interactive mode
            person_names, duration_minutes = prompt_user()
        
        # Find available slots
        event_duration = timedelta(minutes=duration_minutes)
        available_slots = calendar_service.find_available_slots(
            person_names,
            event_duration
        )
        
        # Display results
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
        available_slots: List of datetime.time objects representing available slot start times.
    """
    print(f"\n=== Available Meeting Slots ===")
    print(f"People: {', '.join(person_names)}")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Working hours: 07:00 - 19:00\n")
    
    if not available_slots:
        print("No available slots found for all participants.")
        return
    
    print("Available time slots:")
    for slot_time in available_slots:
        # Calculate end time
        end_minutes = slot_time.hour * 60 + slot_time.minute + duration_minutes
        end_hour = end_minutes // 60
        end_minute = end_minutes % 60
        
        end_time_str = f"{end_hour:02d}:{end_minute:02d}"
        slot_time_str = slot_time.strftime("%H:%M")
        
        print(f"  • {slot_time_str} - {end_time_str}")
    
    print(f"\nTotal: {len(available_slots)} available slot(s)")


if __name__ == "__main__":
    main()
