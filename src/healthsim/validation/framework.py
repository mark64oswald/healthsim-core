"""Core validation framework.

Provides the base classes and data structures for validation throughout
the HealthSim ecosystem.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValidationSeverity(str, Enum):
    """Severity level of a validation issue.

    Attributes:
        ERROR: Critical issue that must be fixed
        WARNING: Potential problem that should be reviewed
        INFO: Informational note, not necessarily a problem
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue.

    Attributes:
        code: Unique identifier for this type of issue (e.g., "DATE_001")
        message: Human-readable description of the issue
        severity: Severity level of the issue
        field_path: Path to the field with the issue (e.g., "person.birth_date")
        context: Additional context about the issue
    """

    code: str
    message: str
    severity: ValidationSeverity
    field_path: str | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return string representation of the issue."""
        location = f" at {self.field_path}" if self.field_path else ""
        return f"[{self.severity.value.upper()}] {self.code}{location}: {self.message}"


@dataclass
class ValidationResult:
    """Result of a validation operation.

    Collects all validation issues found during validation and provides
    convenience methods for checking validity and filtering issues.

    Attributes:
        valid: Whether the validation passed (no errors)
        issues: List of all validation issues found

    Example:
        >>> result = ValidationResult()
        >>> result.add_issue("TEST_001", "Test error", ValidationSeverity.ERROR)
        >>> result.valid
        False
        >>> len(result.errors)
        1
    """

    valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get all ERROR severity issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get all WARNING severity issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    @property
    def infos(self) -> list[ValidationIssue]:
        """Get all INFO severity issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.INFO]

    def add_issue(
        self,
        code: str,
        message: str,
        severity: ValidationSeverity,
        field_path: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Add a validation issue.

        Args:
            code: Unique identifier for this type of issue
            message: Human-readable description
            severity: Severity level
            field_path: Path to the field with the issue
            context: Additional context
        """
        issue = ValidationIssue(
            code=code,
            message=message,
            severity=severity,
            field_path=field_path,
            context=context or {},
        )
        self.issues.append(issue)

        # Mark as invalid if error
        if severity == ValidationSeverity.ERROR:
            self.valid = False

    def merge(self, other: "ValidationResult") -> None:
        """Merge another validation result into this one.

        Args:
            other: Another ValidationResult to merge
        """
        self.issues.extend(other.issues)
        if not other.valid:
            self.valid = False

    def __str__(self) -> str:
        """Return string representation of the result."""
        status = "VALID" if self.valid else "INVALID"
        counts = f"({len(self.errors)} errors, {len(self.warnings)} warnings, {len(self.infos)} info)"
        return f"ValidationResult: {status} {counts}"


class BaseValidator(ABC):
    """Abstract base class for validators.

    Subclasses must implement the validate method to perform
    domain-specific validation.

    Example:
        >>> class AgeValidator(BaseValidator):
        ...     def validate(self, age: int) -> ValidationResult:
        ...         result = ValidationResult()
        ...         if age < 0:
        ...             result.add_issue(
        ...                 code="AGE_001",
        ...                 message="Age cannot be negative",
        ...                 severity=ValidationSeverity.ERROR,
        ...             )
        ...         return result
    """

    @abstractmethod
    def validate(self, *args: Any, **kwargs: Any) -> ValidationResult:
        """Perform validation and return results.

        Returns:
            ValidationResult containing all issues found
        """
        ...
