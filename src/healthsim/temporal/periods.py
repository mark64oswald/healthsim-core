"""Time period handling.

Provides a TimePeriod class for representing spans of time with start and end.
"""

from datetime import datetime, timedelta

from pydantic import BaseModel, field_validator, model_validator


class TimePeriod(BaseModel):
    """A period of time with start and optional end.

    Represents a time span that can be open-ended (no end) or bounded.

    Attributes:
        start: Start datetime of the period
        end: End datetime of the period (None for ongoing)

    Example:
        >>> period = TimePeriod(
        ...     start=datetime(2024, 1, 1, 10, 0),
        ...     end=datetime(2024, 1, 1, 14, 30)
        ... )
        >>> period.duration_hours
        4.5
        >>> period.is_active
        False
    """

    start: datetime
    end: datetime | None = None

    @field_validator("start", "end", mode="before")
    @classmethod
    def parse_datetime(cls, v: str | datetime | None) -> datetime | None:
        """Parse datetime from string if needed."""
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v

    @model_validator(mode="after")
    def validate_end_after_start(self) -> "TimePeriod":
        """Ensure end is after start if both are provided."""
        if self.end is not None and self.end < self.start:
            raise ValueError("end must be after start")
        return self

    @property
    def duration(self) -> timedelta | None:
        """Get the duration of the period.

        Returns:
            Duration as timedelta, or None if period is open-ended
        """
        if self.end is None:
            return None
        return self.end - self.start

    @property
    def duration_hours(self) -> float | None:
        """Get the duration in hours.

        Returns:
            Duration in hours, or None if period is open-ended
        """
        duration = self.duration
        if duration is None:
            return None
        return duration.total_seconds() / 3600

    @property
    def duration_days(self) -> float | None:
        """Get the duration in days.

        Returns:
            Duration in days, or None if period is open-ended
        """
        duration = self.duration
        if duration is None:
            return None
        return duration.total_seconds() / 86400

    @property
    def is_active(self) -> bool:
        """Check if the period is currently active (ongoing or contains now).

        Returns:
            True if period has no end or contains current time
        """
        now = datetime.now()
        if self.end is None:
            return self.start <= now
        return self.start <= now <= self.end

    def contains(self, dt: datetime) -> bool:
        """Check if a datetime falls within this period.

        Args:
            dt: Datetime to check

        Returns:
            True if dt is within the period
        """
        if self.end is None:
            return dt >= self.start
        return self.start <= dt <= self.end

    def overlaps(self, other: "TimePeriod") -> bool:
        """Check if this period overlaps with another.

        Args:
            other: Another TimePeriod to check

        Returns:
            True if the periods overlap
        """
        # If either is open-ended, use a far-future date
        self_end = self.end or datetime.max
        other_end = other.end or datetime.max

        return self.start < other_end and other.start < self_end

    def merge(self, other: "TimePeriod") -> "TimePeriod":
        """Merge this period with another overlapping period.

        Args:
            other: Another TimePeriod to merge

        Returns:
            New TimePeriod spanning both periods

        Raises:
            ValueError: If periods don't overlap
        """
        if not self.overlaps(other):
            raise ValueError("Cannot merge non-overlapping periods")

        new_start = min(self.start, other.start)

        # Handle open-ended periods
        if self.end is None or other.end is None:
            new_end = None
        else:
            new_end = max(self.end, other.end)

        return TimePeriod(start=new_start, end=new_end)
