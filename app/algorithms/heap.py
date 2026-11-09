from typing import Any, List, Optional, Tuple


class MinHeap:
    """
    Min-Heap data structure implementation.

    Time Complexity:
      - Insert (push): O(log n)
      - Extract min (pop): O(log n)
      - Peek: O(1)
      - Heapify: O(n)
    Space Complexity: O(n)

    A binary heap where the parent node is always smaller than its children.
    Used for Priority Scheduling where smaller priority number = higher priority.
    """

    def __init__(self, items: Optional[List[Tuple[Any, ...]]] = None, key_index: int = 0):
        self._heap: List[Tuple[Any, ...]] = []
        self._key_index = key_index
        if items:
            self._heap = list(items)
            self._heapify()

    def __len__(self) -> int:
        return len(self._heap)

    @property
    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def push(self, item: Tuple[Any, ...]) -> None:
        """Insert an item into the heap. O(log n)."""
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def pop(self) -> Optional[Tuple[Any, ...]]:
        """Extract and return the minimum item. O(log n)."""
        if self.is_empty:
            return None
        self._swap(0, len(self._heap) - 1)
        item = self._heap.pop()
        if not self.is_empty:
            self._sift_down(0)
        return item

    def peek(self) -> Optional[Tuple[Any, ...]]:
        """Return the minimum item without removing it. O(1)."""
        if self.is_empty:
            return None
        return self._heap[0]

    def _heapify(self) -> None:
        """Convert an arbitrary list into a heap. O(n)."""
        for i in range(len(self._heap) // 2 - 1, -1, -1):
            self._sift_down(i)

    def _sift_up(self, idx: int) -> None:
        """Move a node up to restore heap property."""
        parent = (idx - 1) // 2
        while idx > 0 and self._compare(idx, parent) < 0:
            self._swap(idx, parent)
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx: int) -> None:
        """Move a node down to restore heap property."""
        n = len(self._heap)
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < n and self._compare(left, smallest) < 0:
                smallest = left
            if right < n and self._compare(right, smallest) < 0:
                smallest = right
            if smallest == idx:
                break
            self._swap(idx, smallest)
            idx = smallest

    def _compare(self, i: int, j: int) -> int:
        """Compare two items by key. Returns negative if i < j."""
        a = self._heap[i][self._key_index]
        b = self._heap[j][self._key_index]
        if a < b:
            return -1
        elif a > b:
            return 1
        return 0

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def to_list(self) -> List[Tuple[Any, ...]]:
        return list(self._heap)


class PriorityQueue:
    """
    Priority Queue implemented using MinHeap.

    Supports (priority, process) pairs where lower priority number = higher priority.
    """

    def __init__(self):
        self._heap = MinHeap([], key_index=0)

    @property
    def is_empty(self) -> bool:
        return self._heap.is_empty

    def enqueue(self, priority: int, item: Any) -> None:
        self._heap.push((priority, item))

    def dequeue(self) -> Optional[Any]:
        result = self._heap.pop()
        if result:
            return result[1]
        return None

    def peek(self) -> Optional[Any]:
        result = self._heap.peek()
        if result:
            return result[1]
        return None
