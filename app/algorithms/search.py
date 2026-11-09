from typing import Any, Callable, List, Optional, TypeVar

from models.inventory import InventoryItem


T = TypeVar("T")


def linear_search(
    items: List[InventoryItem],
    key: str,
    target: Any,
    key_extractor: Optional[Callable[[InventoryItem], Any]] = None,
) -> List[InventoryItem]:
    """
    Linear search algorithm.

    Time Complexity: O(n) - compares each element sequentially.
    Space Complexity: O(1) auxiliary (O(k) for result list).

    Traverses the list from start to end, returning all matching items.
    """
    if key_extractor is None:
        key_extractor = lambda item: getattr(item, key, None)

    results: List[InventoryItem] = []
    for item in items:
        if key_extractor(item) == target:
            results.append(item)
    return results


def linear_search_text(
    items: List[InventoryItem],
    search_term: str,
) -> List[InventoryItem]:
    """
    Linear search with substring matching on name and description.

    Time Complexity: O(n) where n is the number of items.
    Space Complexity: O(k) for results.
    """
    term_lower = search_term.lower().strip()
    if not term_lower:
        return items[:]

    results: List[InventoryItem] = []
    for item in items:
        if term_lower in item.name.lower() or term_lower in item.description.lower():
            results.append(item)
    return results


def binary_search(
    items: List[InventoryItem],
    target_name: str,
) -> Optional[InventoryItem]:
    """
    Binary search algorithm on a sorted list of items by name.

    Time Complexity: O(log n) - halves the search space each iteration.
    Space Complexity: O(1) auxiliary.

    Requires the list to be sorted by name.
    Returns the first matching item or None.
    """
    low, high = 0, len(items) - 1
    target_lower = target_name.lower()

    while low <= high:
        mid = (low + high) // 2
        mid_name = items[mid].name.lower()

        if mid_name == target_lower:
            return items[mid]
        elif mid_name < target_lower:
            low = mid + 1
        else:
            high = mid - 1

    return None


def binary_search_range(
    items: List[InventoryItem],
    min_price: float,
    max_price: float,
) -> List[InventoryItem]:
    """
    Binary search to find items within a price range.

    Time Complexity: O(log n + k) where k is the number of results.
    Space Complexity: O(k) for results.
    """
    if not items:
        return []

    left = 0
    right = len(items) - 1

    while left <= right:
        mid = (left + right) // 2
        if items[mid].price < min_price:
            left = mid + 1
        else:
            right = mid - 1

    start = left
    results: List[InventoryItem] = []
    while start < len(items) and items[start].price <= max_price:
        results.append(items[start])
        start += 1

    return results
