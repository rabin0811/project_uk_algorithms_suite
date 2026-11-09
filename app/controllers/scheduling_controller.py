from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from algorithms.interval import detect_overlaps, find_available_slots, get_schedule_for_day
from algorithms.sort import quick_sort
from models.scheduling import Booking, BookingCollection
from utils.database import DatabaseManager
from utils.helpers import validate_non_empty, validate_time_range
from utils.logger import LoggerSetup


logger = LoggerSetup.get_logger(__name__)


class SchedulingController:
    """Controller handling all scheduling operations and conflict detection."""

    def __init__(self, db: DatabaseManager):
        self._db = db
        self._collection = BookingCollection()
        self._load_from_db()

    def _load_from_db(self) -> None:
        try:
            rows = self._db.get_all("bookings")
            bookings = [Booking.from_dict(row) for row in rows]
            self._collection = BookingCollection(bookings)
            logger.info(f"Loaded {len(bookings)} bookings from database")
        except Exception as e:
            logger.error(f"Failed to load bookings: {e}")

    def book_resource(
        self, resource_name: str, booker_name: str,
        start_time: str, end_time: str, purpose: str
    ) -> Tuple[Optional[Booking], List[Booking]]:
        resource_name = validate_non_empty(resource_name, "Resource name")
        booker_name = validate_non_empty(booker_name, "Booker name")
        validate_time_range(start_time, end_time)

        new_booking = Booking(
            resource_name=resource_name, booker_name=booker_name,
            start_time=start_time, end_time=end_time, purpose=purpose,
        )

        conflicts = self._collection.find_conflicts(new_booking)
        if conflicts:
            logger.warning(f"Conflict detected for {resource_name} at {start_time}")
            return None, conflicts

        now = datetime.now().isoformat()
        booking_data = {
            "resource_name": resource_name, "booker_name": booker_name,
            "start_time": start_time, "end_time": end_time,
            "purpose": purpose, "created_at": now, "updated_at": now,
        }
        booking_id = self._db.insert("bookings", booking_data)
        new_booking.id = booking_id
        new_booking._created_at = now
        new_booking._updated_at = now
        self._collection.add(new_booking)
        logger.info(f"Booked {resource_name} for {booker_name} (id={booking_id})")
        return new_booking, []

    def update_booking(
        self, booking_id: int, resource_name: str, booker_name: str,
        start_time: str, end_time: str, purpose: str
    ) -> Tuple[Optional[Booking], List[Booking]]:
        resource_name = validate_non_empty(resource_name, "Resource name")
        booker_name = validate_non_empty(booker_name, "Booker name")
        validate_time_range(start_time, end_time)

        updated = Booking(
            resource_name=resource_name, booker_name=booker_name,
            start_time=start_time, end_time=end_time, purpose=purpose,
            booking_id=booking_id,
        )

        conflicts = [
            b for b in self._collection.find_conflicts(updated)
            if b.id != booking_id
        ]
        if conflicts:
            logger.warning(f"Conflict detected during update for booking {booking_id}")
            return None, conflicts

        now = datetime.now().isoformat()
        booking_data = {
            "resource_name": resource_name, "booker_name": booker_name,
            "start_time": start_time, "end_time": end_time,
            "purpose": purpose, "updated_at": now,
        }
        self._db.update("bookings", booking_data, booking_id)

        existing = self._collection.get_by_id(booking_id)
        if existing:
            existing.resource_name = resource_name
            existing.booker_name = booker_name
            existing.start_time = start_time
            existing.end_time = end_time
            existing.purpose = purpose

        logger.info(f"Updated booking: id={booking_id}")
        return existing or updated, []

    def delete_booking(self, booking_id: int) -> bool:
        self._db.delete("bookings", booking_id)
        removed = self._collection.remove(booking_id)
        logger.info(f"Deleted booking: id={booking_id}")
        return removed is not None

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        return self._collection.get_by_id(booking_id)

    def get_all_bookings(self) -> List[Booking]:
        return self._collection.bookings

    def get_bookings_for_resource(self, resource_name: str) -> List[Booking]:
        return self._collection.get_bookings_for_resource(resource_name)

    def get_bookings_for_date(self, date_str: str) -> List[Booking]:
        """Get schedule for a specific date using interval algorithm."""
        return get_schedule_for_day(self._collection.bookings, date_str)

    def detect_all_conflicts(self) -> List[Tuple[Booking, Booking]]:
        """Detect all overlapping bookings using interval overlap algorithm."""
        return detect_overlaps(self._collection.bookings)

    def find_available_slots(
        self, resource_name: str, date: str,
        duration_minutes: int = 30,
    ) -> List[Tuple[str, str]]:
        """Find available time slots for a resource on a date."""
        return find_available_slots(
            self._collection.bookings, resource_name, date, duration_minutes
        )

    def search_bookings(self, term: str) -> List[Booking]:
        """Search bookings by resource name or booker name."""
        term_lower = term.lower().strip()
        if not term_lower:
            return self._collection.bookings
        return [
            b for b in self._collection.bookings
            if term_lower in b.resource_name.lower()
            or term_lower in b.booker_name.lower()
            or term_lower in b.purpose.lower()
        ]

    def get_conflict_count(self) -> int:
        return len(self.detect_all_conflicts())

    def get_total_bookings(self) -> int:
        return len(self._collection)
