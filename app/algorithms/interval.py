from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from models.scheduling import Booking


def detect_overlaps(bookings: List[Booking]) -> List[Tuple[Booking, Booking]]:
    """
    Interval overlap detection algorithm.

    Time Complexity: O(n log n) for sorting + O(n) for sweep line.
    Space Complexity: O(n) for storing results and sorted events.

    Uses a sweep line approach: sort all start/end events, then
    sweep through to detect conflicts between intervals.
    """
    conflicts: List[Tuple[Booking, Booking]] = []
    events: List[Tuple[datetime, str, Booking]] = []

    for booking in bookings:
        events.append((booking.start_datetime, "start", booking))
        events.append((booking.end_datetime, "end", booking))

    events.sort(key=lambda e: (e[0], e[1] == "end"))

    active: List[Booking] = []

    for _, event_type, booking in events:
        if event_type == "start":
            for active_booking in active:
                if active_booking.resource_name == booking.resource_name:
                    conflicts.append((active_booking, booking))
            active.append(booking)
        else:
            if booking in active:
                active.remove(booking)

    return conflicts


def find_available_slots(
    bookings: List[Booking],
    resource_name: str,
    date: str,
    slot_duration_minutes: int = 30,
    start_hour: int = 8,
    end_hour: int = 18,
) -> List[Tuple[str, str]]:
    """
    Find available time slots for a resource on a given date.

    Time Complexity: O(n log n) for sorting + O(n) for scanning.
    Space Complexity: O(n) for storing slots.
    """
    resource_bookings = [
        b for b in bookings
        if b.resource_name == resource_name
        and b.start_datetime.strftime("%Y-%m-%d") == date
    ]

    resource_bookings.sort(key=lambda b: b.start_datetime)

    base_dt = datetime.strptime(f"{date} {start_hour}:00", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date} {end_hour}:00", "%Y-%m-%d %H:%M")

    available: List[Tuple[str, str]] = []
    current = base_dt

    for booking in resource_bookings:
        b_start = booking.start_datetime
        b_end = booking.end_datetime

        if current < b_start:
            while current + timedelta(minutes=slot_duration_minutes) <= b_start:
                slot_end_dt = current + timedelta(minutes=slot_duration_minutes)
                available.append((current.isoformat(), slot_end_dt.isoformat()))
                current = slot_end_dt
        current = max(current, b_end)

    while current + timedelta(minutes=slot_duration_minutes) <= end_dt:
        slot_end_dt = current + timedelta(minutes=slot_duration_minutes)
        available.append((current.isoformat(), slot_end_dt.isoformat()))
        current = slot_end_dt

    return available


def sort_bookings_by_time(bookings: List[Booking]) -> List[Booking]:
    """
    Sort bookings by start time.

    Time Complexity: O(n log n).
    Space Complexity: O(n) for sorted copy.
    """
    return sorted(bookings, key=lambda b: b.start_datetime)


def get_schedule_for_day(
    bookings: List[Booking], date: str
) -> List[Booking]:
    """
    Get all bookings for a specific date, sorted by time.
    """
    day_bookings = [b for b in bookings if b.start_datetime.strftime("%Y-%m-%d") == date]
    return sort_bookings_by_time(day_bookings)
