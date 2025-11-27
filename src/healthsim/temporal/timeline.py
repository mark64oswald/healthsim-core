"""Timeline and event management.

Provides classes for managing ordered sequences of events over time.
"""

from datetime import datetime
from typing import Any, Iterator

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """A single event on a timeline.

    Represents a point-in-time event with metadata.

    Attributes:
        event_id: Unique identifier for this event
        event_type: Type/category of the event
        timestamp: When the event occurred
        metadata: Additional data associated with the event

    Example:
        >>> event = TimelineEvent(
        ...     event_id="evt-001",
        ...     event_type="registration",
        ...     timestamp=datetime(2024, 1, 15, 9, 30),
        ...     metadata={"source": "web"}
        ... )
    """

    event_id: str
    event_type: str
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    def __lt__(self, other: "TimelineEvent") -> bool:
        """Compare events by timestamp for sorting."""
        return self.timestamp < other.timestamp


class Timeline(BaseModel):
    """Ordered sequence of events.

    Manages a collection of events for an entity, keeping them in
    chronological order and providing query methods.

    Attributes:
        entity_id: ID of the entity this timeline belongs to
        events: List of events in chronological order

    Example:
        >>> timeline = Timeline(entity_id="person-123")
        >>> timeline.add_event(TimelineEvent(
        ...     event_id="evt-001",
        ...     event_type="created",
        ...     timestamp=datetime(2024, 1, 1)
        ... ))
        >>> timeline.add_event(TimelineEvent(
        ...     event_id="evt-002",
        ...     event_type="updated",
        ...     timestamp=datetime(2024, 1, 15)
        ... ))
        >>> len(timeline)
        2
    """

    entity_id: str
    events: list[TimelineEvent] = Field(default_factory=list)

    def add_event(self, event: TimelineEvent) -> None:
        """Add an event to the timeline.

        The event will be inserted in chronological order.

        Args:
            event: Event to add
        """
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp)

    def get_events_by_type(self, event_type: str) -> list[TimelineEvent]:
        """Get all events of a specific type.

        Args:
            event_type: Type of events to retrieve

        Returns:
            List of matching events in chronological order
        """
        return [e for e in self.events if e.event_type == event_type]

    def get_events_in_range(
        self,
        start: datetime,
        end: datetime,
    ) -> list[TimelineEvent]:
        """Get all events within a time range.

        Args:
            start: Start of the range (inclusive)
            end: End of the range (inclusive)

        Returns:
            List of events within the range
        """
        return [e for e in self.events if start <= e.timestamp <= end]

    def get_event_by_id(self, event_id: str) -> TimelineEvent | None:
        """Get an event by its ID.

        Args:
            event_id: ID of the event to find

        Returns:
            The event if found, None otherwise
        """
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None

    def get_first_event(self) -> TimelineEvent | None:
        """Get the earliest event.

        Returns:
            First event chronologically, or None if empty
        """
        return self.events[0] if self.events else None

    def get_last_event(self) -> TimelineEvent | None:
        """Get the most recent event.

        Returns:
            Last event chronologically, or None if empty
        """
        return self.events[-1] if self.events else None

    def remove_event(self, event_id: str) -> bool:
        """Remove an event by ID.

        Args:
            event_id: ID of the event to remove

        Returns:
            True if event was found and removed, False otherwise
        """
        for i, event in enumerate(self.events):
            if event.event_id == event_id:
                del self.events[i]
                return True
        return False

    def clear(self) -> None:
        """Remove all events from the timeline."""
        self.events.clear()

    def __len__(self) -> int:
        """Return the number of events."""
        return len(self.events)

    def __iter__(self) -> Iterator[TimelineEvent]:
        """Iterate over events in chronological order."""
        return iter(self.events)

    def __contains__(self, event_id: str) -> bool:
        """Check if an event ID exists in the timeline."""
        return any(e.event_id == event_id for e in self.events)
