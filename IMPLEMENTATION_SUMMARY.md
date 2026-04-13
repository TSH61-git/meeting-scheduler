# Calendar Slot Finder - Implementation Summary

## Project Overview
A calendar application that finds available meeting slots for a group of people.
Implements the core requirement from the Comp In-Office Coding Evaluation with clean architecture, dependency injection, and comprehensive testing.

---

## Architecture & Design

### Layered Architecture

#### 1. Models Layer (`io_comp/models/`)
- **Event**: Immutable (`@dataclass(frozen=True)`) domain object
  - Validates `end_time > start_time` on construction via `__post_init__`
  - Utilities: `overlaps_with()`, `duration_minutes()`
- **Person**: Calendar participant with protected state
  - `name` is read-only (property, no setter)
  - `events` returned as copy to prevent external mutation
  - `add_event()` / `remove_event()` are the only mutation points
- **Calendar**: Aggregates people with protected `_people` dict
  - `people` property returns copy to prevent external mutation
  - Working hours removed - managed externally by `WorkingHoursConfig`

#### 2. Configuration (`io_comp/config.py`)
- **WorkingHoursConfig**: Single source of truth for working hours
  - `@dataclass(frozen=True)` - immutable
  - `DEFAULT_WORKING_HOURS = WorkingHoursConfig()` used across all layers

#### 3. Exceptions (`io_comp/exceptions.py`)
- Domain-specific exception hierarchy under `CalendarError`:
  - `PersonNotFoundError` - person not in calendar
  - `InvalidDurationError` - zero, negative, or exceeds working day
  - `InvalidRequestError` - malformed request (e.g. empty person list)
  - `InvalidEventError` - end_time <= start_time
  - `CsvParseError` - CSV format or data errors

#### 4. Data Layer (`io_comp/data/`)
- **CalendarRepository** (Protocol): Abstract interface for data access
- **CSVCalendarRepository**: Implements `CalendarRepository`
  - Parses `Name, Subject, StartTime, EndTime` CSV format
  - Validates time format (HH:MM) and working hours boundaries
  - Row-level error reporting via `CsvParseError`

#### 5. Services Layer (`io_comp/services/`)
- **CalendarService**: Core business logic
  - Receives `CalendarRepository` via constructor (Dependency Injection)
  - Receives `WorkingHoursConfig` via constructor (configurable)
  - `find_available_slots(person_names, event_duration)` - main method
  - Interval merging algorithm (O(n log n))

#### 6. DI Layer (`io_comp/di/`)
- **DIContainer**: Singleton and factory registration
- **create_default_container()**: Wires `CSVCalendarRepository` → `CalendarService`

#### 7. Application Layer (`io_comp/app.py`)
- CLI with interactive and command-line modes
- Specific exception handling per type with user-friendly messages
- Logging to both console and `logs/calendar.log`

---

## Algorithm: Interval Merging

1. Collect busy intervals from all people's events
2. Sort by start time (O(n log n))
3. Merge overlapping/adjacent intervals in single pass
4. Invert to find free intervals within working hours
5. Filter by event duration and return

### Example: Alice & Jack (60 min)
```
Alice: busy 08:00-09:30, 13:00-14:00, 16:00-17:00
Jack:  busy 08:00-08:50, 09:00-09:40, 13:00-14:00, 16:00-17:00
       ↓ merge
Merged: 08:00-09:40, 13:00-14:00, 16:00-17:00
       ↓ invert
Free:   07:00-08:00, 09:40-13:00, 14:00-16:00, 17:00-19:00
       ↓ filter (60 min)
Slots:  07:00, 09:40, 14:00, 17:00 ✓
```

---

## SOLID Principles

| Principle | Implementation |
|-----------|----------------|
| **S**ingle Responsibility | Each class has one job |
| **O**pen/Closed | Add new loaders (JSON, DB) without changing existing code |
| **L**iskov Substitution | `FakeCalendarRepository` replaces `CSVCalendarRepository` in tests |
| **I**nterface Segregation | `CalendarRepository` Protocol exposes only `load()` |
| **D**ependency Inversion | `CalendarService` depends on `CalendarRepository` Protocol, not CSV directly |

---

## Code Quality

- **Immutable models**: `Event` frozen dataclass, `Person.name` read-only, `Calendar.people` copy-on-read
- **Custom exceptions**: Domain-specific hierarchy under `CalendarError`
- **Single config source**: `WorkingHoursConfig` used everywhere
- **Type hints**: All methods fully annotated
- **Logging**: DEBUG for algorithm tracing, INFO for milestones, ERROR for failures - saved to file
- **No CSV dependency in tests**: `FakeCalendarRepository` used in all tests

---

## Testing

- **14 test cases** - 100% pass rate
- **FakeCalendarRepository**: No CSV files needed in tests
- Core functionality, edge cases, error handling all covered

---

## How to Run

```bash
cd python-project
pip install -r requirements.txt
pytest tests/test_app.py        # run tests

python -m io_comp.app           # interactive mode
python -m io_comp.app Alice Jack 60  # CLI mode
```
