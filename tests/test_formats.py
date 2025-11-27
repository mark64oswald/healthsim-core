"""Tests for healthsim.formats module."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from healthsim.formats import BaseTransformer, CSVExporter, JSONExporter
from healthsim.person import Gender, Person, PersonName
from datetime import date


class MockTransformer(BaseTransformer[dict, str]):
    """Mock transformer for testing."""

    def transform(self, source: dict) -> str:
        return f"transformed:{source.get('value', '')}"


class TestBaseTransformer:
    """Tests for BaseTransformer."""

    def test_transform(self) -> None:
        """Test basic transformation."""
        transformer = MockTransformer()
        result = transformer.transform({"value": "test"})
        assert result == "transformed:test"

    def test_transform_batch(self) -> None:
        """Test batch transformation."""
        transformer = MockTransformer()
        sources = [{"value": "a"}, {"value": "b"}, {"value": "c"}]

        results = transformer.transform_batch(sources)

        assert len(results) == 3
        assert results[0] == "transformed:a"
        assert results[1] == "transformed:b"
        assert results[2] == "transformed:c"

    def test_can_transform(self) -> None:
        """Test can_transform default."""
        transformer = MockTransformer()
        assert transformer.can_transform({}) is True


class TestJSONExporter:
    """Tests for JSONExporter."""

    def test_export_dict(self) -> None:
        """Test exporting a dictionary."""
        exporter = JSONExporter()
        data = {"name": "John", "age": 30}

        result = exporter.export(data)
        parsed = json.loads(result)

        assert parsed["name"] == "John"
        assert parsed["age"] == 30

    def test_export_list(self) -> None:
        """Test exporting a list."""
        exporter = JSONExporter()
        data = [1, 2, 3]

        result = exporter.export(data)
        parsed = json.loads(result)

        assert parsed == [1, 2, 3]

    def test_export_pydantic_model(self) -> None:
        """Test exporting a Pydantic model."""
        exporter = JSONExporter()
        person = Person(
            id="test-001",
            name=PersonName(given_name="John", family_name="Smith"),
            birth_date=date(1990, 1, 1),
            gender=Gender.MALE,
        )

        result = exporter.export(person)
        parsed = json.loads(result)

        assert parsed["id"] == "test-001"
        assert parsed["name"]["given_name"] == "John"
        assert parsed["gender"] == "M"

    def test_export_with_indent(self) -> None:
        """Test indented output."""
        exporter = JSONExporter(indent=4)
        data = {"key": "value"}

        result = exporter.export(data)
        assert "    " in result  # Should have 4-space indent

    def test_export_compact(self) -> None:
        """Test compact output."""
        exporter = JSONExporter(indent=None)
        data = {"key": "value"}

        result = exporter.export(data)
        assert "\n" not in result  # No newlines in compact mode

    def test_export_list_of_models(self) -> None:
        """Test exporting list of models."""
        exporter = JSONExporter()
        items = [
            {"name": "a", "value": 1},
            {"name": "b", "value": 2},
        ]

        result = exporter.export_list(items)
        parsed = json.loads(result)

        assert len(parsed) == 2
        assert parsed[0]["name"] == "a"

    def test_export_to_file(self) -> None:
        """Test exporting to file."""
        exporter = JSONExporter()
        data = {"test": "data"}

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            exporter.export_to_file(data, path)

            content = path.read_text()
            parsed = json.loads(content)
            assert parsed["test"] == "data"
        finally:
            path.unlink()


class TestCSVExporter:
    """Tests for CSVExporter."""

    def test_export_list_of_dicts(self) -> None:
        """Test exporting list of dictionaries."""
        exporter = CSVExporter()
        data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25},
        ]

        result = exporter.export(data)
        lines = result.strip().split("\n")

        assert len(lines) == 3  # Header + 2 rows
        assert "name" in lines[0]
        assert "age" in lines[0]
        assert "John" in lines[1]
        assert "Jane" in lines[2]

    def test_export_with_columns(self) -> None:
        """Test exporting with specific column order."""
        exporter = CSVExporter()
        data = [
            {"a": 1, "b": 2, "c": 3},
            {"a": 4, "b": 5, "c": 6},
        ]

        result = exporter.export(data, columns=["c", "a"])
        lines = result.strip().split("\n")

        # Strip \r for cross-platform compatibility (CSV uses \r\n)
        assert lines[0].strip() == "c,a"

    def test_export_without_header(self) -> None:
        """Test exporting without header."""
        exporter = CSVExporter(include_header=False)
        data = [{"name": "John", "age": 30}]

        result = exporter.export(data)
        lines = result.strip().split("\n")

        assert len(lines) == 1
        assert "name" not in lines[0] or "John" in lines[0]

    def test_export_custom_delimiter(self) -> None:
        """Test exporting with custom delimiter."""
        exporter = CSVExporter(delimiter=";")
        data = [{"a": 1, "b": 2}]

        result = exporter.export(data)
        assert ";" in result

    def test_export_empty_data(self) -> None:
        """Test exporting empty data."""
        exporter = CSVExporter()
        result = exporter.export([])
        assert result == ""

    def test_export_to_file(self) -> None:
        """Test exporting to file."""
        exporter = CSVExporter()
        data = [{"x": 1, "y": 2}]

        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            path = Path(f.name)

        try:
            exporter.export_to_file(data, path)
            content = path.read_text()
            assert "x" in content
            assert "y" in content
        finally:
            path.unlink()

    def test_export_handles_none_values(self) -> None:
        """Test that None values are handled."""
        exporter = CSVExporter()
        data = [{"name": "John", "email": None}]

        result = exporter.export(data)
        # Should not raise and should have empty string for None
        assert "John" in result

    def test_flatten_nested_dict(self) -> None:
        """Test flattening nested dictionary."""
        exporter = CSVExporter()
        nested = {"a": {"b": 1, "c": 2}}

        flat = exporter._flatten_dict(nested)

        assert "a_b" in flat
        assert "a_c" in flat
        assert flat["a_b"] == 1
        assert flat["a_c"] == 2