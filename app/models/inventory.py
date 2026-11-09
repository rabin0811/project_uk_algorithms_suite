from datetime import datetime
from typing import Any, Dict, List, Optional


class InventoryItem:
    """Represents a single inventory item with full encapsulation."""

    def __init__(
        self,
        name: str,
        category: str = "General",
        quantity: int = 0,
        price: float = 0.0,
        min_stock_level: int = 5,
        description: str = "",
        item_id: Optional[int] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self._id = item_id
        self._name = name
        self._category = category
        self._quantity = quantity
        self._price = price
        self._min_stock_level = min_stock_level
        self._description = description
        now = datetime.now().isoformat()
        self._created_at = created_at or now
        self._updated_at = updated_at or now

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
        self._updated_at = datetime.now().isoformat()

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        self._category = value
        self._updated_at = datetime.now().isoformat()

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        self._quantity = max(0, value)
        self._updated_at = datetime.now().isoformat()

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        self._price = max(0.0, value)
        self._updated_at = datetime.now().isoformat()

    @property
    def min_stock_level(self) -> int:
        return self._min_stock_level

    @min_stock_level.setter
    def min_stock_level(self, value: int) -> None:
        self._min_stock_level = max(0, value)
        self._updated_at = datetime.now().isoformat()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value
        self._updated_at = datetime.now().isoformat()

    @property
    def is_low_stock(self) -> bool:
        return self._quantity <= self._min_stock_level

    @property
    def stock_status(self) -> str:
        if self._quantity == 0:
            return "Out of Stock"
        elif self.is_low_stock:
            return "Low Stock"
        return "In Stock"

    @property
    def total_value(self) -> float:
        return self._quantity * self._price

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "name": self._name,
            "category": self._category,
            "quantity": self._quantity,
            "price": self._price,
            "min_stock_level": self._min_stock_level,
            "description": self._description,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InventoryItem":
        return cls(
            item_id=data.get("id"),
            name=data.get("name", ""),
            category=data.get("category", "General"),
            quantity=data.get("quantity", 0),
            price=data.get("price", 0.0),
            min_stock_level=data.get("min_stock_level", 5),
            description=data.get("description", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return f"InventoryItem(id={self._id}, name='{self._name}', qty={self._quantity})"


class InventoryCollection:
    """Manages a collection of InventoryItem objects with dictionary and hash-based lookups."""

    def __init__(self, items: Optional[List[InventoryItem]] = None):
        self._items: List[InventoryItem] = items or []
        self._id_index: Dict[int, InventoryItem] = {}
        self._name_index: Dict[str, List[InventoryItem]] = {}
        self._category_index: Dict[str, List[InventoryItem]] = {}
        self._rebuild_indices()

    def _rebuild_indices(self) -> None:
        self._id_index = {}
        self._name_index = {}
        self._category_index = {}
        for item in self._items:
            if item.id is not None:
                self._id_index[item.id] = item
            name_lower = item.name.lower()
            if name_lower not in self._name_index:
                self._name_index[name_lower] = []
            self._name_index[name_lower].append(item)
            cat_lower = item.category.lower()
            if cat_lower not in self._category_index:
                self._category_index[cat_lower] = []
            self._category_index[cat_lower].append(item)

    @property
    def items(self) -> List[InventoryItem]:
        return self._items

    def add(self, item: InventoryItem) -> None:
        self._items.append(item)
        self._rebuild_indices()

    def remove(self, item_id: int) -> Optional[InventoryItem]:
        item = self.get_by_id(item_id)
        if item:
            self._items = [i for i in self._items if i.id != item_id]
            self._rebuild_indices()
        return item

    def get_by_id(self, item_id: int) -> Optional[InventoryItem]:
        return self._id_index.get(item_id)

    def get_by_name(self, name: str) -> List[InventoryItem]:
        return self._name_index.get(name.lower(), [])

    def get_by_category(self, category: str) -> List[InventoryItem]:
        return self._category_index.get(category.lower(), [])

    def get_low_stock_items(self) -> List[InventoryItem]:
        return [item for item in self._items if item.is_low_stock]

    def get_total_value(self) -> float:
        return sum(item.total_value for item in self._items)

    def get_total_items(self) -> int:
        return len(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)
