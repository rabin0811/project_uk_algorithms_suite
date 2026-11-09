from typing import Dict, List, Optional, Tuple

from models.resource_allocation import Process
from algorithms.sort import quick_sort
from algorithms.heap import PriorityQueue


SchedulingResult = Dict[str, List[Dict]]


def first_come_first_served(processes: List[Process]) -> SchedulingResult:
    """
    First Come First Served (FCFS) Scheduling Algorithm.

    Time Complexity: O(n log n) for sorting by arrival time + O(n) for execution.
    Space Complexity: O(n) for the result.

    Processes are executed in order of their arrival time.
    Non-preemptive: once a process starts, it runs to completion.
    """
    if not processes:
        return {"schedule": [], "avg_waiting_time": 0.0, "avg_turnaround_time": 0.0}

    sorted_procs = quick_sort(processes[:], key="arrival_time", reverse=False)
    schedule: List[Dict] = []
    current_time = 0

    for proc in sorted_procs:
        if current_time < proc.arrival_time:
            current_time = proc.arrival_time

        proc.start_time = current_time
        proc.waiting_time = current_time - proc.arrival_time
        proc.completion_time = current_time + proc.burst_time
        proc.turnaround_time = proc.completion_time - proc.arrival_time
        proc.status = "completed"

        schedule.append({
            "process": proc,
            "start": proc.start_time,
            "end": proc.completion_time,
            "waiting_time": proc.waiting_time,
            "turnaround_time": proc.turnaround_time,
        })
        current_time = proc.completion_time

    avg_wait = sum(p.waiting_time for p in sorted_procs) / len(sorted_procs)
    avg_turn = sum(p.turnaround_time for p in sorted_procs) / len(sorted_procs)

    return {
        "schedule": schedule,
        "avg_waiting_time": round(avg_wait, 2),
        "avg_turnaround_time": round(avg_turn, 2),
    }


def shortest_job_first(processes: List[Process]) -> SchedulingResult:
    """
    Shortest Job First (SJF) Non-Preemptive Scheduling Algorithm.

    Time Complexity: O(n^2) in worst case for finding shortest job at each step.
    Space Complexity: O(n) for the result.

    Selects the process with the smallest burst time among available processes.
    """
    if not processes:
        return {"schedule": [], "avg_waiting_time": 0.0, "avg_turnaround_time": 0.0}

    remaining = processes[:]
    schedule: List[Dict] = []
    current_time = 0
    completed_count = 0

    while remaining:
        available = [p for p in remaining if p.arrival_time <= current_time]

        if not available:
            current_time = min(p.arrival_time for p in remaining)
            available = [p for p in remaining if p.arrival_time <= current_time]

        shortest = min(available, key=lambda p: p.burst_time)
        remaining.remove(shortest)

        shortest.start_time = current_time
        shortest.waiting_time = current_time - shortest.arrival_time
        shortest.completion_time = current_time + shortest.burst_time
        shortest.turnaround_time = shortest.completion_time - shortest.arrival_time
        shortest.status = "completed"

        schedule.append({
            "process": shortest,
            "start": shortest.start_time,
            "end": shortest.completion_time,
            "waiting_time": shortest.waiting_time,
            "turnaround_time": shortest.turnaround_time,
        })
        current_time = shortest.completion_time
        completed_count += 1

    avg_wait = sum(s["waiting_time"] for s in schedule) / len(schedule)
    avg_turn = sum(s["turnaround_time"] for s in schedule) / len(schedule)

    return {
        "schedule": schedule,
        "avg_waiting_time": round(avg_wait, 2),
        "avg_turnaround_time": round(avg_turn, 2),
    }


def round_robin(processes: List[Process], time_quantum: int = 4) -> SchedulingResult:
    """
    Round Robin Scheduling Algorithm.

    Time Complexity: O(n) for each cycle, number of cycles depends on burst times.
    Space Complexity: O(n) for the queue and result.

    Each process gets a fixed time quantum in a cyclic order.
    Preemptive: if a process doesn't finish, it goes back to the queue.
    """
    if not processes:
        return {"schedule": [], "avg_waiting_time": 0.0, "avg_turnaround_time": 0.0}

    proc_map = {id(p): p for p in processes}
    remaining_burst = {id(p): p.burst_time for p in processes}
    queue: List[Process] = []
    schedule: List[Dict] = []
    current_time = 0
    completed = set()
    arrival_queue = quick_sort(processes[:], key="arrival_time", reverse=False)

    for proc in arrival_queue:
        proc.status = "pending"

    idx = 0
    while len(completed) < len(processes):
        while idx < len(arrival_queue) and arrival_queue[idx].arrival_time <= current_time:
            pid = id(arrival_queue[idx])
            if pid not in completed and arrival_queue[idx] not in queue:
                queue.append(arrival_queue[idx])
            idx += 1

        if not queue:
            current_time += 1
            continue

        current_proc = queue.pop(0)
        pid = id(current_proc)

        exec_time = min(time_quantum, remaining_burst[pid])
        current_proc.status = "running"

        schedule.append({
            "process": current_proc,
            "start": current_time,
            "end": current_time + exec_time,
            "waiting_time": 0,
            "turnaround_time": 0,
        })

        current_time += exec_time
        remaining_burst[pid] -= exec_time

        while idx < len(arrival_queue) and arrival_queue[idx].arrival_time <= current_time:
            aid = id(arrival_queue[idx])
            if aid not in completed and arrival_queue[idx] not in queue:
                queue.append(arrival_queue[idx])
            idx += 1

        if remaining_burst[pid] == 0:
            current_proc.status = "completed"
            current_proc.completion_time = current_time
            current_proc.turnaround_time = current_time - current_proc.arrival_time
            current_proc.waiting_time = current_proc.turnaround_time - current_proc.burst_time
            completed.add(pid)
        else:
            queue.append(current_proc)

    avg_wait = sum(p.waiting_time for p in processes) / len(processes)
    avg_turn = sum(p.turnaround_time for p in processes) / len(processes)

    return {
        "schedule": schedule,
        "avg_waiting_time": round(avg_wait, 2),
        "avg_turnaround_time": round(avg_turn, 2),
    }


def priority_scheduling(processes: List[Process]) -> SchedulingResult:
    """
    Priority Scheduling Algorithm (Non-Preemptive) using a PriorityQueue (MinHeap).

    Time Complexity: O(n log n) using heap instead of O(n^2) linear scan.
    Space Complexity: O(n) for the heap and result.

    Lower priority number = higher priority.
    Uses a MinHeap-based PriorityQueue for efficient selection.
    """
    if not processes:
        return {"schedule": [], "avg_waiting_time": 0.0, "avg_turnaround_time": 0.0}

    sorted_by_arrival = sorted(processes, key=lambda p: p.arrival_time)
    schedule: List[Dict] = []
    current_time = 0
    idx = 0
    n = len(sorted_by_arrival)
    pq = PriorityQueue()

    while idx < n or not pq.is_empty:
        while idx < n and sorted_by_arrival[idx].arrival_time <= current_time:
            pq.enqueue(sorted_by_arrival[idx].priority, sorted_by_arrival[idx])
            idx += 1

        if pq.is_empty:
            current_time = sorted_by_arrival[idx].arrival_time
            continue

        current_proc = pq.dequeue()

        current_proc.start_time = current_time
        current_proc.waiting_time = current_time - current_proc.arrival_time
        current_proc.completion_time = current_time + current_proc.burst_time
        current_proc.turnaround_time = current_proc.completion_time - current_proc.arrival_time
        current_proc.status = "completed"

        schedule.append({
            "process": current_proc,
            "start": current_proc.start_time,
            "end": current_proc.completion_time,
            "waiting_time": current_proc.waiting_time,
            "turnaround_time": current_proc.turnaround_time,
        })
        current_time = current_proc.completion_time

    avg_wait = sum(s["waiting_time"] for s in schedule) / len(schedule)
    avg_turn = sum(s["turnaround_time"] for s in schedule) / len(schedule)

    return {
        "schedule": schedule,
        "avg_waiting_time": round(avg_wait, 2),
        "avg_turnaround_time": round(avg_turn, 2),
    }
