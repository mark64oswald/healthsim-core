"""Validation framework for HealthSim applications.

This module provides a generic validation framework that can be extended
by products to implement domain-specific validation rules.

Example:
    >>> from healthsim.validation import ValidationResult, ValidationSeverity
    >>>
    >>> result = ValidationResult()
    >>> result.add_issue(
    ...     code="DATE_001",
    ...     message="Date is in the future",
    ...     severity=ValidationSeverity.ERROR,
    ... )
    >>> result.valid
    False
"""

from healthsim.validation.framework import (
    BaseValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)
from healthsim.validation.temporal import TemporalValidator

__all__ = [
    # Core classes
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationResult",
    "BaseValidator",
    # Validators
    "TemporalValidator",
]
