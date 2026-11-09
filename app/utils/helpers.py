import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from utils.logger import LoggerSetup


logger = LoggerSetup.get_logger(__name__)


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load application configuration from config.json and override with .env."""
    config: Dict[str, Any] = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip().lower()
                value = value.strip().strip("\"'")
                mapping = {
                    "database_path": "database_path",
                    "log_level": "log_level",
                    "app_theme": "appearance_mode",
                    "color_theme": "color_theme",
                    "window_width": "window_width",
                    "window_height": "window_height",
                    "sidebar_width": "sidebar_width",
                    "round_robin_time_quantum": "round_robin_time_quantum",
                    "items_per_page": "items_per_page",
                    "low_stock_threshold_percentage": "low_stock_threshold_percentage",
                }
                if key in mapping:
                    int_keys = {"window_width", "window_height", "sidebar_width",
                                "round_robin_time_quantum", "items_per_page",
                                "low_stock_threshold_percentage"}
                    mapped = mapping[key]
                    if mapped in int_keys:
                        try:
                            value = int(value)
                        except ValueError:
                            continue
                    config[mapped] = value
    return config


def validate_positive_integer(value: str, field_name: str) -> int:
    """Validate that a string can be converted to a positive integer."""
    try:
        num = int(value)
        if num < 0:
            raise ValueError(f"{field_name} must be a non-negative integer")
        return num
    except ValueError:
        raise ValueError(f"{field_name} must be a valid integer")


def validate_positive_float(value: str, field_name: str) -> float:
    """Validate that a string can be converted to a positive float."""
    try:
        num = float(value)
        if num < 0:
            raise ValueError(f"{field_name} must be a non-negative number")
        return num
    except ValueError:
        raise ValueError(f"{field_name} must be a valid number")


def validate_non_empty(value: str, field_name: str) -> str:
    """Validate that a string is non-empty."""
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} cannot be empty")
    return stripped


def validate_time_range(start: str, end: str) -> Tuple[datetime, datetime]:
    """Validate that start time is before end time."""
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
    except ValueError:
        raise ValueError("Invalid datetime format. Use ISO format (YYYY-MM-DD HH:MM)")
    if start_dt >= end_dt:
        raise ValueError("Start time must be before end time")
    return start_dt, end_dt


def generate_sample_data() -> Dict[str, List[Dict[str, Any]]]:
    """Generate sample data for demonstration purposes."""
    inventory = [
        {"name": "Laptop Dell XPS 15", "category": "Electronics", "quantity": 15,
         "price": 1299.99, "min_stock_level": 5, "description": "High-performance laptop"},
        {"name": "Office Chair", "category": "Furniture", "quantity": 8,
         "price": 349.50, "min_stock_level": 3, "description": "Ergonomic office chair"},
        {"name": "A4 Paper (Ream)", "category": "Stationery", "quantity": 200,
         "price": 5.99, "min_stock_level": 50, "description": "Premium quality paper"},
        {"name": "Wireless Mouse", "category": "Electronics", "quantity": 3,
         "price": 29.99, "min_stock_level": 10, "description": "Bluetooth mouse"},
        {"name": "Whiteboard Markers (Pack)", "category": "Stationery", "quantity": 25,
         "price": 12.50, "min_stock_level": 10, "description": "Set of 4 markers"},
        {"name": "Desk Lamp", "category": "Furniture", "quantity": 12,
         "price": 45.00, "min_stock_level": 5, "description": "LED desk lamp"},
        {"name": "USB-C Hub", "category": "Electronics", "quantity": 2,
         "price": 39.99, "min_stock_level": 8, "description": "7-in-1 USB-C hub"},
        {"name": "Notebook A5", "category": "Stationery", "quantity": 60,
         "price": 3.99, "min_stock_level": 20, "description": "Hardcover ruled notebook"},
        {"name": "Monitor 27 inch", "category": "Electronics", "quantity": 6,
         "price": 449.99, "min_stock_level": 3, "description": "4K IPS Monitor"},
        {"name": "Standing Desk", "category": "Furniture", "quantity": 4,
         "price": 899.00, "min_stock_level": 2, "description": "Electric height-adjustable"},
    ]

    now = datetime.now()
    bookings = [
        {"resource_name": "Conference Room A", "booker_name": "Dr. Smith",
         "start_time": (now + timedelta(hours=1)).isoformat(),
         "end_time": (now + timedelta(hours=2)).isoformat(),
         "purpose": "Department Meeting"},
        {"resource_name": "Projector Kit", "booker_name": "Alice Johnson",
         "start_time": (now + timedelta(hours=3)).isoformat(),
         "end_time": (now + timedelta(hours=4)).isoformat(),
         "purpose": "Presentation"},
        {"resource_name": "Lab Computer 5", "booker_name": "Bob Williams",
         "start_time": (now + timedelta(days=1, hours=9)).isoformat(),
         "end_time": (now + timedelta(days=1, hours=11)).isoformat(),
         "purpose": "Research Work"},
        {"resource_name": "Conference Room B", "booker_name": "Prof. Davis",
         "start_time": (now + timedelta(hours=2, minutes=30)).isoformat(),
         "end_time": (now + timedelta(hours=3, minutes=30)).isoformat(),
         "purpose": "Student Consultation"},
        {"resource_name": "Audio Equipment", "booker_name": "Event Team",
         "start_time": (now + timedelta(days=2)).isoformat(),
         "end_time": (now + timedelta(days=2, hours=3)).isoformat(),
         "purpose": "University Event"},
    ]

    processes = [
        {"name": "Data Processing A", "burst_time": 6, "priority": 3, "arrival_time": 0},
        {"name": "Web Server B", "burst_time": 8, "priority": 2, "arrival_time": 1},
        {"name": "Database C", "burst_time": 4, "priority": 1, "arrival_time": 2},
        {"name": "Computation D", "burst_time": 10, "priority": 4, "arrival_time": 3},
        {"name": "Report Gen E", "burst_time": 3, "priority": 2, "arrival_time": 4},
    ]

    return {"inventory": inventory, "bookings": bookings, "processes": processes}
