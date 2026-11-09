from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class Booking:
    """Represents a single resource booking with full encapsulation."""

    def __init__(
        self,
        resource_name: str,
        booker_name: str,
        start_time: str,
        end_time: str,
        purpose: str = "",
        booking_id: Optional[int] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self._id = booking_id
        self._resource_name = resource_name
        self._booker_name = booker_name
        self._start_time = start_time
        self._end_time = end_time
        self._purpose = purpose
        now = datetime.now().isoformat()
        self._created_at = created_at or now
        self._updated_at = updated_at or now

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def resource_name(self) -> str:
        return self._resource_name

    @resource_name.setter
    def resource_name(self, value: str) -> None:
        self._resource_name = value
        self._updated_at = datetime.now().isoformat()

    @property
    def booker_name(self) -> str:
        return self._booker_name

    @booker_name.setter
    def booker_name(self, value: str) -> None:
        self._booker_name = value
        self._updated_at = datetime.now().isoformat()

    @property
    def start_time(self) -> str:
        return self._start_time

    @start_time.setter
    def start_time(self, value: str) -> None:
        self._start_time = value
        self._updated_at = datetime.now().isoformat()

    @property
    def end_time(self) -> str:
        return self._end_time

    @end_time.setter
    def end_time(self, value: str) -> None:
        self._end_time = value
        self._updated_at = datetime.now().isoformat()

    @property
    def purpose(self) -> str:
        return self._purpose

    @purpose.setter
    def purpose(self, value: str) -> None:
        self._purpose = value
        self._updated_at = datetime.now().isoformat()

    @property
    def start_datetime(self) -> datetime:
        return datetime.fromisoformat(self._start_time)

    @property
    def end_datetime(self) -> datetime:
        return datetime.fromisoformat(self._end_time)

    @property
    def duration_minutes(self) -> int:
        delta = self.end_datetime - self.start_datetime
        return int(delta.total_seconds() / 60)

    def overlaps_with(self, other: "Booking") -> bool:
        """Check if this booking overlaps with another booking (interval overlap)."""
        return (
            self._resource_name == other._resource_name
            and self.start_datetime < other.end_datetime
            and other.start_datetime < self.end_datetime
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "resource_name": self._resource_name,
            "booker_name": self._booker_name,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "purpose": self._purpose,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Booking":
        return cls(
            booking_id=data.get("id"),
            resource_name=data.get("resource_name", ""),
            booker_name=data.get("booker_name", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            purpose=data.get("purpose", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return f"Booking(id={self._id}, resource='{self._resource_name}', booker='{self._booker_name}')"


class BookingCollection:
    """Manages a collection of Booking objects with conflict detection."""

    def __init__(self, bookings: Optional[List[Booking]] = None):
        self._bookings: List[Booking] = bookings or []

    @property
    def bookings(self) -> List[Booking]:
        return self._bookings

    def add(self, booking: Booking) -> None:
        self._bookings.append(booking)

    def remove(self, booking_id: int) -> Optional[Booking]:
        for i, b in enumerate(self._bookings):
            if b.id == booking_id:
                return self._bookings.pop(i)
        return None

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        for b in self._bookings:
            if b.id == booking_id:
                return b
        return None

    def find_conflicts(self, booking: Booking) -> List[Booking]:
        """Return all bookings that overlap with the given booking."""
        return [b for b in self._bookings if b.id != booking.id and b.overlaps_with(booking)]

    def get_bookings_for_resource(self, resource_name: str) -> List[Booking]:
        return [b for b in self._bookings if b.resource_name == resource_name]

    def get_bookings_for_date(self, date_str: str) -> List[Booking]:
        """Return all bookings occurring on the given date."""
        result = []
        for b in self._bookings:
            b_date = b.start_datetime.strftime("%Y-%m-%d")
            if b_date == date_str:
                result.append(b)
        return result

    def __len__(self) -> int:
        return len(self._bookings)

    def __iter__(self):
        return iter(self._bookings)
