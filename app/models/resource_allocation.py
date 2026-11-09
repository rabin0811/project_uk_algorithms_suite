from datetime import datetime
from typing import Any, Dict, List, Optional


class Process:
    """Represents a process in the CPU scheduling system with full encapsulation."""

    def __init__(
        self,
        name: str,
        burst_time: int = 1,
        priority: int = 1,
        arrival_time: int = 0,
        status: str = "pending",
        process_id: Optional[int] = None,
        remaining_time: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        self._id = process_id
        self._name = name
        self._burst_time = max(1, burst_time)
        self._priority = max(0, priority)
        self._arrival_time = max(0, arrival_time)
        self._status = status
        self._remaining_time = remaining_time if remaining_time is not None else self._burst_time
        self._created_at = created_at or datetime.now().isoformat()
        self._waiting_time: int = 0
        self._turnaround_time: int = 0
        self._completion_time: int = 0
        self._start_time: int = 0

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def burst_time(self) -> int:
        return self._burst_time

    @burst_time.setter
    def burst_time(self, value: int) -> None:
        self._burst_time = max(1, value)
        self._remaining_time = self._burst_time

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, value: int) -> None:
        self._priority = max(0, value)

    @property
    def arrival_time(self) -> int:
        return self._arrival_time

    @arrival_time.setter
    def arrival_time(self, value: int) -> None:
        self._arrival_time = max(0, value)

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def remaining_time(self) -> int:
        return self._remaining_time

    @remaining_time.setter
    def remaining_time(self, value: int) -> None:
        self._remaining_time = max(0, value)

    @property
    def waiting_time(self) -> int:
        return self._waiting_time

    @waiting_time.setter
    def waiting_time(self, value: int) -> None:
        self._waiting_time = value

    @property
    def turnaround_time(self) -> int:
        return self._turnaround_time

    @turnaround_time.setter
    def turnaround_time(self, value: int) -> None:
        self._turnaround_time = value

    @property
    def completion_time(self) -> int:
        return self._completion_time

    @completion_time.setter
    def completion_time(self, value: int) -> None:
        self._completion_time = value

    @property
    def start_time(self) -> int:
        return self._start_time

    @start_time.setter
    def start_time(self, value: int) -> None:
        self._start_time = value

    def is_completed(self) -> bool:
        return self._status == "completed"

    def is_running(self) -> bool:
        return self._status == "running"

    def is_pending(self) -> bool:
        return self._status == "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "name": self._name,
            "burst_time": self._burst_time,
            "priority": self._priority,
            "arrival_time": self._arrival_time,
            "status": self._status,
            "remaining_time": self._remaining_time,
            "created_at": self._created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Process":
        return cls(
            process_id=data.get("id"),
            name=data.get("name", ""),
            burst_time=data.get("burst_time", 1),
            priority=data.get("priority", 1),
            arrival_time=data.get("arrival_time", 0),
            status=data.get("status", "pending"),
            remaining_time=data.get("remaining_time"),
            created_at=data.get("created_at"),
        )

    def __repr__(self) -> str:
        return f"Process(id={self._id}, name='{self._name}', burst={self._burst_time}, priority={self._priority})"


class ProcessQueue:
    """Manages a collection of processes using a queue-like structure."""

    def __init__(self, processes: Optional[List[Process]] = None):
        self._processes: List[Process] = processes or []

    @property
    def processes(self) -> List[Process]:
        return self._processes

    def enqueue(self, process: Process) -> None:
        self._processes.append(process)

    def dequeue(self) -> Optional[Process]:
        if self._processes:
            return self._processes.pop(0)
        return None

    def peek(self) -> Optional[Process]:
        if self._processes:
            return self._processes[0]
        return None

    def remove(self, process_id: int) -> Optional[Process]:
        for i, p in enumerate(self._processes):
            if p.id == process_id:
                return self._processes.pop(i)
        return None

    def get_by_id(self, process_id: int) -> Optional[Process]:
        for p in self._processes:
            if p.id == process_id:
                return p
        return None

    def get_pending(self) -> List[Process]:
        return [p for p in self._processes if p.is_pending()]

    def get_completed(self) -> List[Process]:
        return [p for p in self._processes if p.is_completed()]

    def get_running(self) -> List[Process]:
        return [p for p in self._processes if p.is_running()]

    def clear_completed(self) -> None:
        self._processes = [p for p in self._processes if not p.is_completed()]

    @property
    def is_empty(self) -> bool:
        return len(self._processes) == 0

    @property
    def size(self) -> int:
        return len(self._processes)

    def __len__(self) -> int:
        return len(self._processes)

    def __iter__(self):
        return iter(self._processes)
