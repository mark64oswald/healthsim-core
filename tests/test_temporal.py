"""Tests for healthsim.temporal module."""

import random
from datetime import date, datetime, timedelta

import pytest

from healthsim.temporal import (
    TimePeriod,
    Timeline,
    TimelineEvent,
    calculate_age,
    format_date_iso,
    format_datetime_iso,
    parse_date,
    parse_datetime,
    random_date_in_range,
    random_datetime_in_range,
)


class TestTimePeriod:
    """Tests for TimePeriod."""

    def test_creation(self) -> None:
        """Test creating a time period."""
        period = TimePeriod(
            start=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 1, 14, 0),
        )

        assert period.start == datetime(2024, 1, 1, 10, 0)
        assert period.end == datetime(2024, 1, 1, 14, 0)

    def test_open_ended_period(self) -> None:
        """Test period without end date."""
        period = TimePeriod(start=datetime(2024, 1, 1, 10, 0))

        assert period.end is None
        assert period.duration is None

    def test_duration(self) -> None:
        """Test duration calculation."""
        period = TimePeriod(
            start=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 1, 14, 30),
        )

        assert period.duration == timedelta(hours=4, minutes=30)
        assert period.duration_hours == 4.5

    def test_duration_days(self) -> None:
        """Test duration in days."""
        period = TimePeriod(
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 8),
        )

        assert period.duration_days == 7.0

    def test_end_must_be_after_start(self) -> None:
        """Test that end must be after start."""
        with pytest.raises(ValueError, match="end must be after start"):
            TimePeriod(
                start=datetime(2024, 1, 2),
                end=datetime(2024, 1, 1),
            )

    def test_contains(self) -> None:
        """Test contains method."""
        period = TimePeriod(
            start=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 1, 14, 0),
        )

        assert period.contains(datetime(2024, 1, 1, 12, 0)) is True
        assert period.contains(datetime(2024, 1, 1, 8, 0)) is False
        assert period.contains(datetime(2024, 1, 1, 16, 0)) is False

    def test_contains_open_ended(self) -> None:
        """Test contains for open-ended period."""
        period = TimePeriod(start=datetime(2024, 1, 1, 10, 0))

        assert period.contains(datetime(2024, 1, 1, 12, 0)) is True
        assert period.contains(datetime(2024, 12, 31, 23, 59)) is True
        assert period.contains(datetime(2024, 1, 1, 8, 0)) is False

    def test_overlaps(self) -> None:
        """Test overlaps method."""
        period1 = TimePeriod(
            start=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 1, 14, 0),
        )
        period2 = TimePeriod(
            start=datetime(2024, 1, 1, 12, 0),
            end=datetime(2024, 1, 1, 16, 0),
        )
        period3 = TimePeriod(
            start=datetime(2024, 1, 1, 15, 0),
            end=datetime(2024, 1, 1, 17, 0),
        )

        assert period1.overlaps(period2) is True
        assert period1.overlaps(period3) is False

    def test_merge(self) -> None:
        """Test merging overlapping periods."""
        period1 = TimePeriod(
            start=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 1, 14, 0),
        )
        period2 = TimePeriod(
            start=datetime(2024, 1, 1, 12, 0),
            end=datetime(2024, 1, 1, 16, 0),
        )

        merged = period1.merge(period2)

        assert merged.start == datetime(2024, 1, 1, 10, 0)
        assert merged.end == datetime(2024, 1, 1, 16, 0)

    def test_merge_non_overlapping_raises(self) -> None:
        """Test merging non-overlapping periods raises error."""
        period1 = TimePeriod(
            start=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 1, 12, 0),
        )
        period2 = TimePeriod(
            start=datetime(2024, 1, 1, 14, 0),
            end=datetime(2024, 1, 1, 16, 0),
        )

        with pytest.raises(ValueError, match="non-overlapping"):
            period1.merge(period2)


class TestTimelineEvent:
    """Tests for TimelineEvent."""

    def test_creation(self) -> None:
        """Test creating an event."""
        event = TimelineEvent(
            event_id="evt-001",
            event_type="registration",
            timestamp=datetime(2024, 1, 15, 9, 30),
            metadata={"source": "web"},
        )

        assert event.event_id == "evt-001"
        assert event.event_type == "registration"
        assert event.metadata == {"source": "web"}

    def test_comparison(self) -> None:
        """Test event comparison by timestamp."""
        event1 = TimelineEvent(
            event_id="1",
            event_type="a",
            timestamp=datetime(2024, 1, 1),
        )
        event2 = TimelineEvent(
            event_id="2",
            event_type="b",
            timestamp=datetime(2024, 1, 2),
        )

        assert event1 < event2


class TestTimeline:
    """Tests for Timeline."""

    def test_creation(self) -> None:
        """Test creating a timeline."""
        timeline = Timeline(entity_id="person-123")

        assert timeline.entity_id == "person-123"
        assert len(timeline) == 0

    def test_add_event(self) -> None:
        """Test adding events."""
        timeline = Timeline(entity_id="person-123")
        event = TimelineEvent(
            event_id="evt-001",
            event_type="created",
            timestamp=datetime(2024, 1, 1),
        )

        timeline.add_event(event)

        assert len(timeline) == 1
        assert timeline.get_first_event() == event

    def test_events_sorted(self) -> None:
        """Test events are kept in chronological order."""
        timeline = Timeline(entity_id="test")

        timeline.add_event(TimelineEvent(
            event_id="2",
            event_type="b",
            timestamp=datetime(2024, 1, 15),
        ))
        timeline.add_event(TimelineEvent(
            event_id="1",
            event_type="a",
            timestamp=datetime(2024, 1, 1),
        ))
        timeline.add_event(TimelineEvent(
            event_id="3",
            event_type="c",
            timestamp=datetime(2024, 1, 10),
        ))

        events = list(timeline)
        assert events[0].event_id == "1"
        assert events[1].event_id == "3"
        assert events[2].event_id == "2"

    def test_get_events_by_type(self) -> None:
        """Test filtering events by type."""
        timeline = Timeline(entity_id="test")
        timeline.add_event(TimelineEvent(
            event_id="1",
            event_type="login",
            timestamp=datetime(2024, 1, 1),
        ))
        timeline.add_event(TimelineEvent(
            event_id="2",
            event_type="purchase",
            timestamp=datetime(2024, 1, 2),
        ))
        timeline.add_event(TimelineEvent(
            event_id="3",
            event_type="login",
            timestamp=datetime(2024, 1, 3),
        ))

        logins = timeline.get_events_by_type("login")
        assert len(logins) == 2

    def test_get_events_in_range(self) -> None:
        """Test getting events in time range."""
        timeline = Timeline(entity_id="test")
        timeline.add_event(TimelineEvent(
            event_id="1",
            event_type="a",
            timestamp=datetime(2024, 1, 1),
        ))
        timeline.add_event(TimelineEvent(
            event_id="2",
            event_type="b",
            timestamp=datetime(2024, 1, 15),
        ))
        timeline.add_event(TimelineEvent(
            event_id="3",
            event_type="c",
            timestamp=datetime(2024, 2, 1),
        ))

        events = timeline.get_events_in_range(
            start=datetime(2024, 1, 10),
            end=datetime(2024, 1, 20),
        )

        assert len(events) == 1
        assert events[0].event_id == "2"

    def test_remove_event(self) -> None:
        """Test removing an event."""
        timeline = Timeline(entity_id="test")
        timeline.add_event(TimelineEvent(
            event_id="1",
            event_type="a",
            timestamp=datetime(2024, 1, 1),
        ))

        assert timeline.remove_event("1") is True
        assert len(timeline) == 0
        assert timeline.remove_event("1") is False

    def test_contains(self) -> None:
        """Test contains check."""
        timeline = Timeline(entity_id="test")
        timeline.add_event(TimelineEvent(
            event_id="evt-123",
            event_type="test",
            timestamp=datetime(2024, 1, 1),
        ))

        assert "evt-123" in timeline
        assert "evt-456" not in timeline


class TestTemporalUtils:
    """Tests for temporal utility functions."""

    def test_calculate_age(self) -> None:
        """Test age calculation."""
        # Test with known dates
        age = calculate_age(date(1990, 6, 15), date(2024, 1, 1))
        assert age == 33

        # Birthday not yet occurred this year
        age = calculate_age(date(1990, 6, 15), date(2024, 6, 1))
        assert age == 33

        # After birthday
        age = calculate_age(date(1990, 6, 15), date(2024, 7, 1))
        assert age == 34

    def test_format_datetime_iso(self) -> None:
        """Test ISO datetime formatting."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_iso(dt)
        assert formatted == "2024-01-15T14:30:00"

    def test_format_date_iso(self) -> None:
        """Test ISO date formatting."""
        d = date(2024, 1, 15)
        formatted = format_date_iso(d)
        assert formatted == "2024-01-15"

    def test_parse_datetime(self) -> None:
        """Test datetime parsing."""
        dt = parse_datetime("2024-01-15T14:30:00")
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 14
        assert dt.minute == 30

    def test_parse_date(self) -> None:
        """Test date parsing."""
        d = parse_date("2024-01-15")
        assert d == date(2024, 1, 15)

    def test_random_date_in_range(self) -> None:
        """Test random date generation."""
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        rng = random.Random(42)

        d = random_date_in_range(start, end, rng)

        assert start <= d <= end

    def test_random_date_reproducibility(self) -> None:
        """Test reproducibility with same seed."""
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)

        rng1 = random.Random(42)
        rng2 = random.Random(42)

        d1 = random_date_in_range(start, end, rng1)
        d2 = random_date_in_range(start, end, rng2)

        assert d1 == d2

    def test_random_datetime_in_range(self) -> None:
        """Test random datetime generation."""
        start = datetime(2024, 1, 1, 0, 0)
        end = datetime(2024, 1, 1, 23, 59)
        rng = random.Random(42)

        dt = random_datetime_in_range(start, end, rng)

        assert start <= dt <= end