from typing import Any, Callable, List, TypeVar

from models.inventory import InventoryItem


T = TypeVar("T")


def merge_sort(
    items: List[InventoryItem],
    key: str = "name",
    reverse: bool = False,
) -> List[InventoryItem]:
    """
    Merge Sort algorithm.

    Time Complexity: O(n log n) in all cases.
    Space Complexity: O(n) auxiliary space for merging.

    Divide and conquer: splits array in half, recursively sorts, then merges.
    """
    if len(items) <= 1:
        return items

    mid = len(items) // 2
    left = merge_sort(items[:mid], key, reverse)
    right = merge_sort(items[mid:], key, reverse)

    return _merge(left, right, key, reverse)


def _merge(
    left: List[InventoryItem],
    right: List[InventoryItem],
    key: str,
    reverse: bool,
) -> List[InventoryItem]:
    result: List[InventoryItem] = []
    i = j = 0

    key_extractor = lambda item: (
        getattr(item, key).lower() if isinstance(getattr(item, key, ""), str)
        else getattr(item, key, 0)
    )

    while i < len(left) and j < len(right):
        left_val = key_extractor(left[i])
        right_val = key_extractor(right[j])
        condition = left_val <= right_val if not reverse else left_val >= right_val
        if condition:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(
    items: List[InventoryItem],
    key: str = "quantity",
    reverse: bool = False,
) -> List[InventoryItem]:
    """
    Quick Sort algorithm.

    Time Complexity: O(n log n) average, O(n^2) worst case.
    Space Complexity: O(log n) auxiliary for recursion stack.

    Uses the last element as pivot and partitions around it.
    """
    if len(items) <= 1:
        return items

    key_extractor = lambda item: (
        getattr(item, key).lower() if isinstance(getattr(item, key, ""), str)
        else getattr(item, key, 0)
    )

    pivot = items[-1]
    pivot_val = key_extractor(pivot)

    left: List[InventoryItem] = []
    right: List[InventoryItem] = []
    middle: List[InventoryItem] = []

    for item in items:
        val = key_extractor(item)
        if val < pivot_val:
            left.append(item)
        elif val > pivot_val:
            right.append(item)
        else:
            middle.append(item)

    if reverse:
        return quick_sort(right, key, reverse) + middle + quick_sort(left, key, reverse)
    return quick_sort(left, key, reverse) + middle + quick_sort(right, key, reverse)
