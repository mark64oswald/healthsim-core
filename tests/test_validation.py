"""Tests for healthsim.validation module."""

from datetime import date, datetime, timedelta

import pytest

from healthsim.validation import (
    BaseValidator,
    TemporalValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)


class TestValidationSeverity:
    """Tests for ValidationSeverity enum."""

    def test_values(self) -> None:
        """Test enum values."""
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.INFO.value == "info"


class TestValidationIssue:
    """Tests for ValidationIssue."""

    def test_creation(self) -> None:
        """Test creating a validation issue."""
        issue = ValidationIssue(
            code="TEST_001",
            message="Test message",
            severity=ValidationSeverity.ERROR,
            field_path="test.field",
            context={"key": "value"},
        )

        assert issue.code == "TEST_001"
        assert issue.message == "Test message"
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.field_path == "test.field"
        assert issue.context == {"key": "value"}

    def test_str_representation(self) -> None:
        """Test string representation."""
        issue = ValidationIssue(
            code="ERR_001",
            message="Something went wrong",
            severity=ValidationSeverity.ERROR,
            field_path="data.field",
        )

        str_repr = str(issue)
        assert "ERROR" in str_repr
        assert "ERR_001" in str_repr
        assert "data.field" in str_repr
        assert "Something went wrong" in str_repr

    def test_default_context(self) -> None:
        """Test default empty context."""
        issue = ValidationIssue(
            code="TEST",
            message="Test",
            severity=ValidationSeverity.INFO,
        )
        assert issue.context == {}
        assert issue.field_path is None


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_initial_state(self) -> None:
        """Test initial state is valid."""
        result = ValidationResult()
        assert result.valid is True
        assert result.issues == []

    def test_add_error_marks_invalid(self) -> None:
        """Test adding error marks result invalid."""
        result = ValidationResult()
        result.add_issue(
            code="ERR_001",
            message="Error message",
            severity=ValidationSeverity.ERROR,
        )

        assert result.valid is False
        assert len(result.issues) == 1

    def test_add_warning_keeps_valid(self) -> None:
        """Test adding warning keeps result valid."""
        result = ValidationResult()
        result.add_issue(
            code="WARN_001",
            message="Warning message",
            severity=ValidationSeverity.WARNING,
        )

        assert result.valid is True
        assert len(result.issues) == 1

    def test_errors_property(self) -> None:
        """Test errors property filters correctly."""
        result = ValidationResult()
        result.add_issue("ERR_1", "Error 1", ValidationSeverity.ERROR)
        result.add_issue("WARN_1", "Warning 1", ValidationSeverity.WARNING)
        result.add_issue("ERR_2", "Error 2", ValidationSeverity.ERROR)
        result.add_issue("INFO_1", "Info 1", ValidationSeverity.INFO)

        assert len(result.errors) == 2
        assert all(e.severity == ValidationSeverity.ERROR for e in result.errors)

    def test_warnings_property(self) -> None:
        """Test warnings property filters correctly."""
        result = ValidationResult()
        result.add_issue("ERR_1", "Error 1", ValidationSeverity.ERROR)
        result.add_issue("WARN_1", "Warning 1", ValidationSeverity.WARNING)
        result.add_issue("WARN_2", "Warning 2", ValidationSeverity.WARNING)

        assert len(result.warnings) == 2
        assert all(w.severity == ValidationSeverity.WARNING for w in result.warnings)

    def test_infos_property(self) -> None:
        """Test infos property filters correctly."""
        result = ValidationResult()
        result.add_issue("INFO_1", "Info 1", ValidationSeverity.INFO)
        result.add_issue("ERR_1", "Error 1", ValidationSeverity.ERROR)

        assert len(result.infos) == 1
        assert result.infos[0].code == "INFO_1"

    def test_merge(self) -> None:
        """Test merging validation results."""
        result1 = ValidationResult()
        result1.add_issue("ERR_1", "Error 1", ValidationSeverity.ERROR)

        result2 = ValidationResult()
        result2.add_issue("WARN_1", "Warning 1", ValidationSeverity.WARNING)

        result1.merge(result2)

        assert len(result1.issues) == 2
        assert result1.valid is False

    def test_merge_valid_into_valid(self) -> None:
        """Test merging two valid results."""
        result1 = ValidationResult()
        result1.add_issue("INFO_1", "Info 1", ValidationSeverity.INFO)

        result2 = ValidationResult()
        result2.add_issue("WARN_1", "Warning 1", ValidationSeverity.WARNING)

        result1.merge(result2)

        assert result1.valid is True
        assert len(result1.issues) == 2

    def test_str_representation(self) -> None:
        """Test string representation."""
        result = ValidationResult()
        result.add_issue("ERR_1", "Error", ValidationSeverity.ERROR)
        result.add_issue("WARN_1", "Warning", ValidationSeverity.WARNING)

        str_repr = str(result)
        assert "INVALID" in str_repr
        assert "1 errors" in str_repr
        assert "1 warnings" in str_repr


class TestTemporalValidator:
    """Tests for TemporalValidator."""

    def test_date_not_future_valid(self) -> None:
        """Test validating a past date."""
        validator = TemporalValidator()
        result = validator.validate_date_not_future(
            d=date(2020, 1, 1),
            field_name="test_date",
        )

        assert result.valid is True
        assert len(result.issues) == 0

    def test_date_not_future_invalid(self) -> None:
        """Test validating a future date."""
        validator = TemporalValidator()
        future_date = date.today() + timedelta(days=30)
        result = validator.validate_date_not_future(
            d=future_date,
            field_name="test_date",
        )

        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "TEMP_001"

    def test_date_not_future_with_reference(self) -> None:
        """Test with custom reference date."""
        validator = TemporalValidator()
        result = validator.validate_date_not_future(
            d=date(2024, 6, 1),
            field_name="test_date",
            as_of=date(2024, 1, 1),
        )

        assert result.valid is False

    def test_date_order_valid(self) -> None:
        """Test valid date order."""
        validator = TemporalValidator()
        result = validator.validate_date_order(
            earlier=date(2020, 1, 1),
            later=date(2020, 12, 31),
            earlier_field="start",
            later_field="end",
        )

        assert result.valid is True

    def test_date_order_invalid(self) -> None:
        """Test invalid date order."""
        validator = TemporalValidator()
        result = validator.validate_date_order(
            earlier=date(2020, 12, 31),
            later=date(2020, 1, 1),
            earlier_field="start",
            later_field="end",
        )

        assert result.valid is False
        assert result.errors[0].code == "TEMP_002"

    def test_date_order_with_none(self) -> None:
        """Test date order with None values."""
        validator = TemporalValidator()
        result = validator.validate_date_order(
            earlier=None,
            later=date(2020, 1, 1),
            earlier_field="start",
            later_field="end",
        )

        assert result.valid is True  # Can't validate with None

    def test_date_order_allow_equal(self) -> None:
        """Test date order with equal dates allowed."""
        validator = TemporalValidator()
        same_date = date(2020, 6, 15)

        result = validator.validate_date_order(
            earlier=same_date,
            later=same_date,
            earlier_field="start",
            later_field="end",
            allow_equal=True,
        )
        assert result.valid is True

        result = validator.validate_date_order(
            earlier=same_date,
            later=same_date,
            earlier_field="start",
            later_field="end",
            allow_equal=False,
        )
        assert result.valid is False

    def test_duration_valid(self) -> None:
        """Test valid duration."""
        validator = TemporalValidator()
        result = validator.validate_duration(
            start=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 1, 14, 0),
            max_duration=timedelta(hours=8),
        )

        assert result.valid is True

    def test_duration_negative(self) -> None:
        """Test negative duration."""
        validator = TemporalValidator()
        result = validator.validate_duration(
            start=datetime(2024, 1, 1, 14, 0),
            end=datetime(2024, 1, 1, 10, 0),
        )

        assert result.valid is False
        assert result.errors[0].code == "TEMP_003"

    def test_duration_exceeds_max(self) -> None:
        """Test duration exceeding maximum."""
        validator = TemporalValidator()
        result = validator.validate_duration(
            start=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 2, 10, 0),
            max_duration=timedelta(hours=8),
        )

        assert len(result.warnings) == 1
        assert result.warnings[0].code == "TEMP_004"

    def test_age_range_valid(self) -> None:
        """Test valid age range."""
        validator = TemporalValidator()
        birth_date = date.today() - timedelta(days=365 * 30)  # ~30 years old

        result = validator.validate_age_range(
            birth_date=birth_date,
            min_age=18,
            max_age=65,
        )

        assert result.valid is True

    def test_age_range_too_young(self) -> None:
        """Test age below minimum."""
        validator = TemporalValidator()
        birth_date = date.today() - timedelta(days=365 * 10)  # ~10 years old

        result = validator.validate_age_range(
            birth_date=birth_date,
            min_age=18,
            max_age=65,
        )

        assert result.valid is False
        assert result.errors[0].code == "TEMP_006"

    def test_age_range_too_old(self) -> None:
        """Test age above maximum."""
        validator = TemporalValidator()
        birth_date = date.today() - timedelta(days=365 * 200)  # ~200 years old

        result = validator.validate_age_range(
            birth_date=birth_date,
            min_age=0,
            max_age=150,
        )

        assert len(result.warnings) == 1
        assert result.warnings[0].code == "TEMP_007"