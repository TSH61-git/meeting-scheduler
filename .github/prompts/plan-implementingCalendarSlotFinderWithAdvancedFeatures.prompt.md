## Plan: Implementing Calendar Slot Finder with Advanced Features

Build a modular calendar application with object-oriented design, efficient interval merging algorithm for slot finding, minute-level precision, additional layers (services and data), dependency injection for decoupling, comprehensive tests, and strict working hours validation to meet all exercise requirements.

**Steps**
1. **Phase 1: Design Data Models** - Create Event, Person, and Calendar classes with proper encapsulation and relationships. Implement time handling with minute precision using datetime.time.
2. **Phase 2: Implement Data Layer** - Build a CSVDataLoader class to parse calendar.csv, validate data, and load into Calendar model. Handle edge cases like invalid times or formats.
3. **Phase 3: Develop Services Layer** - Create a CalendarService class to encapsulate business logic, including the core find_available_slots method using a simple and clear interval merging algorithm.
4. **Phase 4: Implement Core Algorithm** - In CalendarService, merge overlapping events per person, find intersection of free times across all persons, filter by event duration, and return available start times with strict validation within 07:00-19:00 working hours.
5. **Phase 5: Integrate Dependency Injection** - Implement a simple DI container or injector to manage dependencies (e.g., inject CalendarService into app.py, DataLoader into Service). Use interfaces for abstractions.
6. **Phase 6: Update Main Application** - Modify app.py to use DI for injecting services and data loaders, provide command-line interface for input/output.
7. **Phase 7: Write Comprehensive Tests** - Implement 2-3 critical tests in test_app.py: example case (Alice & Jack, 60 min), no-conflict case, and no-slots case. Add edge case tests for overlapping events, boundary times, and working hours validation.
8. **Phase 8: Add Logging and Error Handling** - Integrate logging for debugging slot calculations, add input validation and meaningful error messages, especially for working hours.
9. **Phase 9: Final Review and Refinement** - Ensure SOLID principles, meaningful naming, extensibility, and DI integration throughout.

**Relevant files & folder structure**
- `io_comp/app.py` — Main application entry point, integrate DI and services
- `io_comp/__init__.py` — Package initialization
- `resources/calendar.csv` — Input data file (already exists)

Folders by layer:
- `io_comp/models/` — Data models (Event, Person, Calendar)
  - `__init__.py`
  - `event.py`
  - `person.py`
  - `calendar.py`
- `io_comp/data/` — Data layer and loaders
  - `__init__.py`
  - `csv_loader.py` (formerly data_loader)
- `io_comp/services/` — Business logic and algorithm
  - `__init__.py`
  - `calendar_service.py`
- `io_comp/di/` — Dependency injection container and interfaces (container.py will implement a simple registry/locator)
  - `__init__.py`
  - `container.py`
  - `interfaces.py`
- `tests/test_app.py` — Test cases for the functionality

**Verification**
1. Run tests: `pytest tests/test_app.py` to ensure all test cases pass, including the example output and working hours validation.
2. Manual test: Execute the app with example inputs and verify output matches README example, with DI properly injecting dependencies.
3. Code quality: Check for PEP 8 compliance, meaningful names, SOLID adherence, and DI decoupling via code review.
4. Edge cases: Test with invalid CSV data, times outside working hours, and DI configuration to confirm error handling.

**Decisions**
- Algorithm: Use simple and clear interval merging (sort events, merge overlaps) for efficiency (O(n log n) time complexity) to handle overlapping events and find free slots.
- Precision: Minute-level using datetime.time objects for exact time handling; results will be returned as a list of `datetime.time` objects representing slot start times, or optionally tuples of `(start_time, end_time)` when ranges are required.
- Additional layers: Services layer for business logic separation, data layer for loading/parsing, DI for decoupling and testability. DI container resides in `io_comp/di/container.py`.
- Working Hours Validation: Strict enforcement - slots must start and end within 07:00-19:00, with clear error messages for violations.
- Time zones: Plan for timezone awareness by normalizing all times to UTC internally and converting to local zones on output.
- Scope: Focus on single-day calendar as per requirements; no multi-day or date handling initially.

**Further Considerations**
1. Extensibility: Design interfaces for data sources and services to allow easy addition of JSON or database loaders in the future, facilitated by DI.
