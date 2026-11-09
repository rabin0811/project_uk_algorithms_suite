import sqlite3
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from utils.logger import LoggerSetup


logger = LoggerSetup.get_logger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and schema initialization."""

    def __init__(self, db_path: str = "data/management_suite.db"):
        self.db_path = db_path
        self._ensure_data_directory()
        self.connection: Optional[sqlite3.Connection] = None
        self.connect()

    def _ensure_data_directory(self) -> None:
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def connect(self) -> None:
        """Establish database connection with row factory for dict-like access."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        logger.info(f"Database connected: {self.db_path}")

    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()
            logger.info("Database disconnected")

    def initialize_tables(self) -> None:
        """Create all required tables if they do not exist."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'General',
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0.0,
                min_stock_level INTEGER NOT NULL DEFAULT 5,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_name TEXT NOT NULL,
                booker_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                purpose TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                burst_time INTEGER NOT NULL DEFAULT 1,
                priority INTEGER NOT NULL DEFAULT 1,
                arrival_time INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                remaining_time INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        ]
        cursor = self.connection.cursor()
        for query in queries:
            cursor.execute(query)
        self.connection.commit()
        logger.info("Database tables initialized")

    def execute_query(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> sqlite3.Cursor:
        """Execute a single query with optional parameters."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Query failed: {query[:60]}... Error: {e}")
            raise

    def fetch_all(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> List[Dict[str, Any]]:
        """Fetch all rows as dictionaries."""
        cursor = self.execute_query(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def fetch_one(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single row as a dictionary."""
        cursor = self.execute_query(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a record and return the new row ID."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.execute_query(query, values)
        logger.debug(f"Inserted into {table}: id={cursor.lastrowid}")
        return cursor.lastrowid

    def update(self, table: str, data: Dict[str, Any], record_id: int) -> None:
        """Update a record by ID."""
        set_clause = ", ".join(f"{k} = ?" for k in data.keys())
        values = tuple(data.values()) + (record_id,)
        query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        self.execute_query(query, values)
        logger.debug(f"Updated {table}: id={record_id}")

    def delete(self, table: str, record_id: int) -> None:
        """Delete a record by ID."""
        query = f"DELETE FROM {table} WHERE id = ?"
        self.execute_query(query, (record_id,))
        logger.debug(f"Deleted from {table}: id={record_id}")

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        """Retrieve all records from a table."""
        return self.fetch_all(f"SELECT * FROM {table} ORDER BY id DESC")

    def get_by_id(self, table: str, record_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single record by ID."""
        return self.fetch_one(f"SELECT * FROM {table} WHERE id = ?", (record_id,))

    def search(self, table: str, column: str, term: str) -> List[Dict[str, Any]]:
        """Search records where a column contains the given term."""
        pattern = f"%{term}%"
        return self.fetch_all(
            f"SELECT * FROM {table} WHERE {column} LIKE ? ORDER BY id DESC",
            (pattern,)
        )
