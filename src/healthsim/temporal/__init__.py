"""Temporal data structures and utilities.

This module provides timeline management, period handling, and date utilities
for temporal data in HealthSim applications.
"""

from healthsim.temporal.periods import TimePeriod
from healthsim.temporal.timeline import Timeline, TimelineEvent
from healthsim.temporal.utils import (
    calculate_age,
    format_date_iso,
    format_datetime_iso,
    parse_date,
    parse_datetime,
    random_date_in_range,
    random_datetime_in_range,
)

__all__ = [
    # Period handling
    "TimePeriod",
    # Timeline
    "Timeline",
    "TimelineEvent",
    # Utilities
    "calculate_age",
    "format_datetime_iso",
    "format_date_iso",
    "parse_datetime",
    "parse_date",
    "random_date_in_range",
    "random_datetime_in_range",
]
