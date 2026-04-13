"""
Calendar application entry point.
Finds available meeting slots for a group of people using the DI container.
"""

import sys
import logging
from datetime import time, timedelta
from pathlib import Path
from typing import List, Tuple

from io_comp.di.container import create_default_container
from io_comp.exceptions import (
    PersonNotFoundError, InvalidDurationError, InvalidRequestError, CsvParseError
)


def _configure_logging() -> None:
    """Configure logging to both console and file."""
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logs_dir / "calendar.log"),
        ]
    )


_configure_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point - load calendar, resolve inputs, find and display available slots."""
    try:
        csv_file_path = Path(__file__).parent.parent / "resources" / "calendar.csv"

        logger.info("Initializing application...")
        calendar_service = create_default_container(str(csv_file_path)).get("calendar_service")

        person_names, duration_minutes = _resolve_inputs()

        logger.info(f"Searching slots for {person_names}, duration={duration_minutes} min")
        available_slots = calendar_service.find_available_slots(
            person_names, timedelta(minutes=duration_minutes)
        )
        display_results(person_names, duration_minutes, available_slots)

    except FileNotFoundError as e:
        logger.error(e)
        print(f"❌ File not found: {e}")
        sys.exit(1)
    except CsvParseError as e:
        logger.error(e)
        print(f"❌ Failed to load calendar: {e}")
        sys.exit(1)
    except PersonNotFoundError as e:
        logger.error(e)
        print(f"❌ Person not found: {e}")
        sys.exit(1)
    except InvalidDurationError as e:
        logger.error(e)
        print(f"❌ Invalid duration: {e}")
        sys.exit(1)
    except InvalidRequestError as e:
        logger.error(e)
        print(f"❌ Invalid request: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(e)
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def _resolve_inputs() -> Tuple[List[str], int]:
    """Return (person_names, duration_minutes) from CLI args or interactive prompt."""
    if len(sys.argv) > 1:
        return _parse_args(sys.argv[1:])
    return _prompt_user()


def _parse_args(args: List[str]) -> Tuple[List[str], int]:
    """Parse CLI arguments in format: name1 name2 ... duration_minutes."""
    if len(args) < 2:
        raise InvalidRequestError(
            "Usage: python -m io_comp.app [person1] [person2] ... [duration_minutes]\n"
            "Example: python -m io_comp.app Alice Jack 60"
        )
    try:
        duration_minutes = int(args[-1])
        person_names = args[:-1]
        if duration_minutes <= 0:
            raise InvalidDurationError("Duration must be positive")
        return person_names, duration_minutes
    except ValueError:
        raise InvalidRequestError(f"Duration must be a number, got: '{args[-1]}'")


def _prompt_user() -> Tuple[List[str], int]:
    """Prompt the user interactively for person names and meeting duration."""
    print("\n=== Calendar Available Slots Finder ===\n")

    while True:
        names_input = input("Enter person names (comma-separated): ").strip()
        person_names = [n.strip() for n in names_input.split(",") if n.strip()]
        if person_names:
            break
        print("Please enter at least one name.")

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


def display_results(
    person_names: List[str],
    duration_minutes: int,
    available_slots: List[Tuple[time, time]]
) -> None:
    """Display available slots in a user-friendly format."""
    print(f"\n=== Available Meeting Slots ===")
    print(f"People: {', '.join(person_names)}")
    print(f"Duration: {duration_minutes} minutes\n")

    if not available_slots:
        print("No available slots found for all participants.")
        return

    for start_time, end_time in available_slots:
        start_str = start_time.strftime("%H:%M")
        end_minutes = end_time.hour * 60 + end_time.minute
        latest_start = end_minutes - duration_minutes
        latest_start_str = f"{latest_start // 60:02d}:{latest_start % 60:02d}"

        if start_str == latest_start_str:
            print(f"Starting Time of available slots: {start_str}")
        else:
            print(f"Starting Time of available slots: {start_str} - {latest_start_str}")

    print(f"\nTotal: {len(available_slots)} available slot(s)")


if __name__ == "__main__":
    main()
