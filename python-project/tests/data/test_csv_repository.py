"""
Tests for CSVCalendarRepository.
"""

import pytest
from pathlib import Path

from io_comp.data.csv_loader import CSVCalendarRepository
from io_comp.exceptions import CsvParseError


@pytest.fixture
def tmp_csv(tmp_path: Path):
    """Helper to create a temporary CSV file with given content."""
    def _make(content: str) -> str:
        csv_file = tmp_path / "calendar.csv"
        csv_file.write_text(content, encoding="utf-8")
        return str(csv_file)
    return _make


class TestCSVCalendarRepository:

    def test_load_valid_csv(self, tmp_csv):
        """Valid CSV loads correctly into Calendar."""
        path = tmp_csv('Alice,"Morning meeting",08:00,09:30\n')
        calendar = CSVCalendarRepository(path).load()
        assert calendar.person_count() == 1
        assert calendar.get_person("Alice") is not None
        assert len(calendar.get_person("Alice").events) == 1

    def test_load_multiple_people(self, tmp_csv):
        """Multiple people are loaded correctly."""
        path = tmp_csv(
            'Alice,"Meeting",08:00,09:00\n'
            'Bob,"Lunch",13:00,14:00\n'
        )
        calendar = CSVCalendarRepository(path).load()
        assert calendar.person_count() == 2

    def test_load_same_person_multiple_events(self, tmp_csv):
        """Multiple rows for same person accumulate events."""
        path = tmp_csv(
            'Alice,"Meeting",08:00,09:00\n'
            'Alice,"Lunch",13:00,14:00\n'
        )
        calendar = CSVCalendarRepository(path).load()
        assert calendar.person_count() == 1
        assert len(calendar.get_person("Alice").events) == 2

    def test_file_not_found_raises(self):
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            CSVCalendarRepository("nonexistent.csv").load()

    def test_wrong_column_count_raises(self, tmp_csv):
        """Row with wrong number of columns raises CsvParseError."""
        path = tmp_csv('Alice,"Meeting",08:00\n')
        with pytest.raises(CsvParseError):
            CSVCalendarRepository(path).load()

    def test_empty_name_raises(self, tmp_csv):
        """Empty person name raises CsvParseError."""
        path = tmp_csv(',"Meeting",08:00,09:00\n')
        with pytest.raises(CsvParseError):
            CSVCalendarRepository(path).load()

    def test_empty_subject_raises(self, tmp_csv):
        """Empty event subject raises CsvParseError."""
        path = tmp_csv('Alice,"",08:00,09:00\n')
        with pytest.raises(CsvParseError):
            CSVCalendarRepository(path).load()

    def test_invalid_time_format_raises(self, tmp_csv):
        """Invalid time format raises CsvParseError."""
        path = tmp_csv('Alice,"Meeting",8am,9am\n')
        with pytest.raises(CsvParseError):
            CSVCalendarRepository(path).load()

    def test_time_outside_working_hours_raises(self, tmp_csv):
        """Time outside working hours raises CsvParseError."""
        path = tmp_csv('Alice,"Meeting",06:00,07:00\n')
        with pytest.raises(CsvParseError):
            CSVCalendarRepository(path).load()

    def test_empty_rows_are_skipped(self, tmp_csv):
        """Empty rows in CSV are skipped without error."""
        path = tmp_csv(
            'Alice,"Meeting",08:00,09:00\n'
            '\n'
            'Bob,"Lunch",13:00,14:00\n'
        )
        calendar = CSVCalendarRepository(path).load()
        assert calendar.person_count() == 2
