"""
Dependency Injection container for managing application dependencies.
"""

from typing import Any, Callable, Dict
import logging

from io_comp.data import CSVCalendarRepository
from io_comp.services import CalendarService


logger = logging.getLogger(__name__)


class DIContainer:
    """Simple DI container supporting singleton and factory registrations."""

    def __init__(self) -> None:
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}

    def register_singleton(self, key: str, instance: Any) -> None:
        """Register a shared singleton instance under the given key."""
        self._singletons[key] = instance
        logger.debug(f"Registered singleton: {key}")

    def register_factory(self, key: str, factory: Callable[[], Any]) -> None:
        """Register a factory function that creates a new instance on each call."""
        self._factories[key] = factory
        logger.debug(f"Registered factory: {key}")

    def get(self, key: str) -> Any:
        """Return the dependency registered under key. Raises KeyError if not found."""
        if key in self._singletons:
            return self._singletons[key]
        if key in self._factories:
            return self._factories[key]()
        raise KeyError(f"Dependency '{key}' not registered in DI container")

    def clear(self) -> None:
        """Remove all registered dependencies."""
        self._singletons.clear()
        self._factories.clear()
        logger.debug("Cleared all dependencies from DI container")


def create_default_container(csv_file_path: str) -> DIContainer:
    """Create and configure the default DI container with all standard components."""
    container = DIContainer()
    repo = CSVCalendarRepository(csv_file_path)
    service = CalendarService(repo)
    container.register_singleton("calendar_service", service)
    logger.info("CalendarService created and registered successfully")
    logger.info("DI container configured successfully")
    return container
