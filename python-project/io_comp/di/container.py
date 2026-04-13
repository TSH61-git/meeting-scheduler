"""
Dependency Injection container for managing application dependencies.
"""

from typing import Any, Callable, Dict, Optional
import logging

from io_comp.data import CSVCalendarRepository
from io_comp.services import CalendarService


logger = logging.getLogger(__name__)


class DIContainer:
    """
    Simple dependency injection container for managing application dependencies.
    
    Supports:
    - Singleton registration (one instance shared across app)
    - Factory registration (new instance on each request)
    - Lazy initialization (create on first access)
    """

    def __init__(self):
        """Initialize an empty DI container."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}

    def register_singleton(self, key: str, instance: Any) -> None:
        """
        Register a singleton instance.
        
        Args:
            key: The key by which to retrieve the instance.
            instance: The instance to register.
        """
        self._singletons[key] = instance
        logger.debug(f"Registered singleton: {key}")

    def register_factory(self, key: str, factory: Callable[[], Any]) -> None:
        """
        Register a factory function that creates new instances.
        
        Args:
            key: The key by which to retrieve instances.
            factory: A callable that returns a new instance when called.
        """
        self._factories[key] = factory
        logger.debug(f"Registered factory: {key}")

    def get(self, key: str) -> Any:
        """
        Retrieve a registered dependency.
        
        Args:
            key: The key of the dependency to retrieve.
            
        Returns:
            The singleton instance or a new instance from the factory.
            
        Raises:
            KeyError: If the key is not registered.
        """
        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]
        
        # Check factories
        if key in self._factories:
            return self._factories[key]()
        
        raise KeyError(f"Dependency '{key}' not registered in DI container")

    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._singletons.clear()
        self._factories.clear()
        logger.debug("Cleared all dependencies from DI container")


def create_default_container(csv_file_path: str) -> DIContainer:
    """
    Create and configure the default DI container with all standard components.
    
    Args:
        csv_file_path: Path to the calendar CSV file.
        
    Returns:
        A fully configured DIContainer.
    """
    container = DIContainer()
    
    repo = CSVCalendarRepository(csv_file_path)
    service = CalendarService(repo)
    container.register_singleton("calendar_service", service)
    logger.info("CalendarService created and registered successfully")
    
    logger.info("DI container configured successfully")
    return container
