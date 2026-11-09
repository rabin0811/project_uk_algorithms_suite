from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from algorithms.search import linear_search, linear_search_text, binary_search
from algorithms.sort import merge_sort, quick_sort
from models.inventory import InventoryCollection, InventoryItem
from utils.database import DatabaseManager
from utils.helpers import validate_non_empty, validate_positive_float, validate_positive_integer
from utils.logger import LoggerSetup


logger = LoggerSetup.get_logger(__name__)


class InventoryController:
    """Controller handling all inventory operations and algorithm orchestration."""

    def __init__(self, db: DatabaseManager):
        self._db = db
        self._collection = InventoryCollection()
        self._load_from_db()

    def _load_from_db(self) -> None:
        try:
            rows = self._db.get_all("inventory_items")
            items = [InventoryItem.from_dict(row) for row in rows]
            self._collection = InventoryCollection(items)
            logger.info(f"Loaded {len(items)} inventory items from database")
        except Exception as e:
            logger.error(f"Failed to load inventory: {e}")

    def add_item(
        self, name: str, category: str, quantity: int,
        price: float, min_stock_level: int, description: str
    ) -> InventoryItem:
        name = validate_non_empty(name, "Name")
        quantity = validate_positive_integer(str(quantity), "Quantity")
        price = validate_positive_float(str(price), "Price")
        min_stock_val = validate_positive_integer(str(min_stock_level), "Minimum stock level")

        now = datetime.now().isoformat()
        item_data = {
            "name": name, "category": category, "quantity": quantity,
            "price": price, "min_stock_level": min_stock_val,
            "description": description, "created_at": now, "updated_at": now,
        }
        item_id = self._db.insert("inventory_items", item_data)
        item = InventoryItem(
            item_id=item_id, name=name, category=category,
            quantity=quantity, price=price, min_stock_level=min_stock_val,
            description=description, created_at=now, updated_at=now,
        )
        self._collection.add(item)
        logger.info(f"Added inventory item: {name} (id={item_id})")
        return item

    def update_item(
        self, item_id: int, name: str, category: str, quantity: int,
        price: float, min_stock_level: int, description: str
    ) -> Optional[InventoryItem]:
        name = validate_non_empty(name, "Name")
        quantity = validate_positive_integer(str(quantity), "Quantity")
        price = validate_positive_float(str(price), "Price")
        min_stock_val = validate_positive_integer(str(min_stock_level), "Minimum stock level")

        now = datetime.now().isoformat()
        item_data = {
            "name": name, "category": category, "quantity": quantity,
            "price": price, "min_stock_level": min_stock_val,
            "description": description, "updated_at": now,
        }
        self._db.update("inventory_items", item_data, item_id)

        item = self._collection.get_by_id(item_id)
        if item:
            item.name = name
            item.category = category
            item.quantity = quantity
            item.price = price
            item.min_stock_level = min_stock_val
            item.description = description

        logger.info(f"Updated inventory item: id={item_id}")
        return item

    def delete_item(self, item_id: int) -> bool:
        self._db.delete("inventory_items", item_id)
        removed = self._collection.remove(item_id)
        logger.info(f"Deleted inventory item: id={item_id}")
        return removed is not None

    def get_item(self, item_id: int) -> Optional[InventoryItem]:
        return self._collection.get_by_id(item_id)

    def get_all_items(self) -> List[InventoryItem]:
        return self._collection.items

    def search_items(self, term: str) -> List[InventoryItem]:
        """Search inventory using linear search with substring matching."""
        return linear_search_text(self._collection.items, term)

    def search_exact(self, field: str, value: Any) -> List[InventoryItem]:
        """Search using linear search with exact matching."""
        return linear_search(self._collection.items, field, value)

    def search_binary(self, name: str) -> Optional[InventoryItem]:
        """Search using binary search (requires sorted list)."""
        sorted_items = self.get_sorted_by_name()
        return binary_search(sorted_items, name)

    def get_sorted_by_name(self, reverse: bool = False) -> List[InventoryItem]:
        """Sort items by name using Merge Sort."""
        return merge_sort(self._collection.items[:], key="name", reverse=reverse)

    def get_sorted_by_quantity(self, reverse: bool = False) -> List[InventoryItem]:
        """Sort items by quantity using Quick Sort."""
        return quick_sort(self._collection.items[:], key="quantity", reverse=reverse)

    def get_sorted_by_price(self, reverse: bool = False) -> List[InventoryItem]:
        """Sort items by price using Merge Sort."""
        return merge_sort(self._collection.items[:], key="price", reverse=reverse)

    def get_low_stock_items(self) -> List[InventoryItem]:
        return self._collection.get_low_stock_items()

    def get_low_stock_count(self) -> int:
        return len(self._collection.get_low_stock_items())

    def get_total_value(self) -> float:
        return self._collection.get_total_value()

    def get_total_items(self) -> int:
        return self._collection.get_total_items()

    def get_category_summary(self) -> Dict[str, Dict[str, Any]]:
        """Generate a summary of inventory categories."""
        summary: Dict[str, Dict[str, Any]] = {}
        for item in self._collection:
            if item.category not in summary:
                summary[item.category] = {
                    "count": 0, "total_value": 0.0, "total_quantity": 0
                }
            summary[item.category]["count"] += 1
            summary[item.category]["total_value"] += item.total_value
            summary[item.category]["total_quantity"] += item.quantity
        return summary

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive inventory report."""
        return {
            "total_items": self.get_total_items(),
            "total_value": round(self.get_total_value(), 2),
            "low_stock_count": self.get_low_stock_count(),
            "categories": self.get_category_summary(),
            "items": [item.to_dict() for item in self._collection.items],
            "generated_at": datetime.now().isoformat(),
        }
