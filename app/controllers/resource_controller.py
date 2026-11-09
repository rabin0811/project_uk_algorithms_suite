from datetime import datetime
from typing import Any, Dict, List, Optional

from algorithms.scheduling_algo import (
    SchedulingResult,
    first_come_first_served,
    priority_scheduling,
    round_robin,
    shortest_job_first,
)
from models.resource_allocation import Process, ProcessQueue
from utils.database import DatabaseManager
from utils.helpers import validate_non_empty, validate_positive_integer
from utils.logger import LoggerSetup


logger = LoggerSetup.get_logger(__name__)


class ResourceController:
    """Controller handling all resource allocation operations and algorithm execution."""

    def __init__(self, db: DatabaseManager):
        self._db = db
        self._queue = ProcessQueue()
        self._load_from_db()

    def _load_from_db(self) -> None:
        try:
            rows = self._db.get_all("processes")
            processes = [Process.from_dict(row) for row in rows]
            self._queue = ProcessQueue(processes)
            logger.info(f"Loaded {len(processes)} processes from database")
        except Exception as e:
            logger.error(f"Failed to load processes: {e}")

    def add_process(
        self, name: str, burst_time: int,
        priority: int = 1, arrival_time: int = 0,
    ) -> Process:
        name = validate_non_empty(name, "Process name")
        burst_time = validate_positive_integer(str(burst_time), "Burst time")
        priority = validate_positive_integer(str(priority), "Priority")
        arrival_time = validate_positive_integer(str(arrival_time), "Arrival time")

        now = datetime.now().isoformat()
        process_data = {
            "name": name, "burst_time": burst_time, "priority": priority,
            "arrival_time": arrival_time, "status": "pending",
            "remaining_time": burst_time, "created_at": now,
        }
        proc_id = self._db.insert("processes", process_data)
        process = Process(
            process_id=proc_id, name=name, burst_time=burst_time,
            priority=priority, arrival_time=arrival_time,
            status="pending", remaining_time=burst_time, created_at=now,
        )
        self._queue.enqueue(process)
        logger.info(f"Added process: {name} (id={proc_id})")
        return process

    def remove_process(self, process_id: int) -> bool:
        self._db.delete("processes", process_id)
        removed = self._queue.remove(process_id)
        logger.info(f"Removed process: id={process_id}")
        return removed is not None

    def get_process(self, process_id: int) -> Optional[Process]:
        return self._queue.get_by_id(process_id)

    def get_all_processes(self) -> List[Process]:
        return self._queue.processes

    def get_pending_processes(self) -> List[Process]:
        return self._queue.get_pending()

    def get_completed_processes(self) -> List[Process]:
        return self._queue.get_completed()

    def clear_completed(self) -> None:
        self._queue.clear_completed()
        self._db.execute_query(
            "DELETE FROM processes WHERE status = 'completed'"
        )
        logger.info("Cleared completed processes")

    def run_fcfs(self) -> SchedulingResult:
        """Execute First Come First Served scheduling algorithm."""
        logger.info("Running FCFS scheduling")
        return first_come_first_served(self._queue.processes[:])

    def run_sjf(self) -> SchedulingResult:
        """Execute Shortest Job First scheduling algorithm."""
        logger.info("Running SJF scheduling")
        return shortest_job_first(self._queue.processes[:])

    def run_round_robin(self, time_quantum: int = 4) -> SchedulingResult:
        """Execute Round Robin scheduling algorithm."""
        logger.info(f"Running Round Robin (quantum={time_quantum})")
        return round_robin(self._queue.processes[:], time_quantum)

    def run_priority(self) -> SchedulingResult:
        """Execute Priority scheduling algorithm."""
        logger.info("Running Priority scheduling")
        return priority_scheduling(self._queue.processes[:])

    def get_queue_size(self) -> int:
        return self._queue.size

    def get_process_count(self) -> int:
        return len(self._queue)
