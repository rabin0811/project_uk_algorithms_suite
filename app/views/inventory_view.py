from typing import Any, Dict, List, Optional

import customtkinter as ctk

from controllers.inventory_controller import InventoryController
from models.inventory import InventoryItem
from views.components import (
    CardFrame,
    ComplexityCard,
    ConfirmDialog,
    InfoDialog,
    SectionHeader,
    TableView,
    Tooltip,
)


class InventoryView(ctk.CTkFrame):
    """Inventory management view with full CRUD, search, sort and reporting."""

    def __init__(self, master, controller: InventoryController, **kwargs):
        super().__init__(master, **kwargs)
        self._controller = controller
        self._current_sort_key = "name"
        self._current_sort_reverse = False
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        self._scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll_frame.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            self._scroll_frame, title="Inventory Management",
            subtitle="Add, edit, delete and search inventory items"
        ).pack(fill="x", pady=(0, 20))

        self._build_toolbar()
        self._build_table()
        self._build_low_stock_alert()
        self._build_stats_bar()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        left = ctk.CTkFrame(toolbar, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        self._search_var = ctk.StringVar()
        self._search_var.trace("w", lambda *a: self._on_search())
        self._search_entry = ctk.CTkEntry(
            left, placeholder_text="Search items...", width=300,
            font=ctk.CTkFont(size=13),
        )
        self._search_entry.pack(side="left", padx=(0, 8))
        self._search_entry.configure(textvariable=self._search_var)
        Tooltip(self._search_entry, "Search by name or description (Linear Search)")

        sort_options = ["Name", "Quantity", "Price", "Category"]
        self._sort_combo = ctk.CTkOptionMenu(
            left, values=sort_options, command=self._on_sort_change,
            width=140, font=ctk.CTkFont(size=13),
        )
        self._sort_combo.pack(side="left", padx=(0, 8))
        Tooltip(self._sort_combo, "Sort items (Merge Sort / Quick Sort)")

        self._reverse_btn = ctk.CTkButton(
            left, text="\u2191\u2193", width=40, command=self._toggle_sort_order,
            font=ctk.CTkFont(size=16),
        )
        self._reverse_btn.pack(side="left")
        Tooltip(self._reverse_btn, "Toggle ascending/descending")

        right = ctk.CTkFrame(toolbar, fg_color="transparent")
        right.pack(side="right")

        self._add_btn = ctk.CTkButton(
            right, text="+  Add Item", width=120, command=self._show_add_dialog,
            font=ctk.CTkFont(size=13), fg_color="#2d8a4e", hover_color="#236b3d",
        )
        self._add_btn.pack(side="left", padx=(0, 8))
        Tooltip(self._add_btn, "Add a new inventory item")

        self._import_btn = ctk.CTkButton(
            right, text="Import Sample", width=120, command=self._import_sample,
            font=ctk.CTkFont(size=12), fg_color="#555555",
        )
        self._import_btn.pack(side="left", padx=(0, 8))
        Tooltip(self._import_btn, "Load sample inventory data")

        self._report_btn = ctk.CTkButton(
            right, text="Report", width=100, command=self._show_report,
            font=ctk.CTkFont(size=13), fg_color="#6a1f8d", hover_color="#551a73",
        )
        self._report_btn.pack(side="left")
        Tooltip(self._report_btn, "Generate inventory report")

    def _build_table(self) -> None:
        self._table_frame = CardFrame(
            self._scroll_frame, title="Inventory Items", width=0, height=420,
        )
        self._table_frame.pack(fill="x", pady=(0, 12))

        columns = ["ID", "Name", "Category", "Quantity", "Price", "Min Stock", "Status", "Total Value"]
        widths = [50, 200, 120, 80, 90, 90, 100, 110]
        self._table = TableView(
            self._table_frame.content, columns=columns, column_widths=widths,
            height=350,
        )
        self._table.pack(fill="both", expand=True)
        self._table.on_select(self._on_row_select)

        btn_frame = ctk.CTkFrame(self._table_frame.content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 0))

        self._edit_btn = ctk.CTkButton(
            btn_frame, text="Edit Selected", width=120,
            command=self._show_edit_dialog, state="disabled",
            font=ctk.CTkFont(size=12),
        )
        self._edit_btn.pack(side="left", padx=(0, 8))
        Tooltip(self._edit_btn, "Edit the selected item")

        self._delete_btn = ctk.CTkButton(
            btn_frame, text="Delete Selected", width=120,
            command=self._confirm_delete, state="disabled",
            font=ctk.CTkFont(size=12), fg_color="#a83232", hover_color="#8a2828",
        )
        self._delete_btn.pack(side="left")
        Tooltip(self._delete_btn, "Delete the selected item")

    def _build_low_stock_alert(self) -> None:
        self._low_stock_frame = CardFrame(
            self._scroll_frame, title="Low Stock Alerts", width=0, height=100,
        )
        self._low_stock_frame.pack(fill="x", pady=(0, 12))
        self._low_stock_label = ctk.CTkLabel(
            self._low_stock_frame.content, text="",
            font=ctk.CTkFont(size=13), anchor="w",
        )
        self._low_stock_label.pack(fill="x", padx=8, pady=8)

    def _build_stats_bar(self) -> None:
        stats_frame = CardFrame(
            self._scroll_frame, title="Statistics", width=0, height=80,
        )
        stats_frame.pack(fill="x", pady=(0, 12))

        self._stats_label = ctk.CTkLabel(
            stats_frame.content, text="",
            font=ctk.CTkFont(size=13), anchor="w",
        )
        self._stats_label.pack(fill="x", padx=8, pady=8)

        algo_info = [
            {"name": "Linear Search", "time": "O(n)", "space": "O(1)"},
            {"name": "Binary Search", "time": "O(log n)", "space": "O(1)"},
            {"name": "Merge Sort", "time": "O(n log n)", "space": "O(n)"},
            {"name": "Quick Sort", "time": "O(n log n) avg", "space": "O(log n)"},
        ]
        self._complexity_card = ComplexityCard(
            self._scroll_frame, complexities=algo_info,
        )
        self._complexity_card.pack(fill="x")

    def _on_search(self) -> None:
        self._refresh_table()

    def _on_sort_change(self, choice: str) -> None:
        key_map = {"Name": "name", "Quantity": "quantity", "Price": "price", "Category": "category"}
        self._current_sort_key = key_map.get(choice, "name")
        self._refresh_table()

    def _toggle_sort_order(self) -> None:
        self._current_sort_reverse = not self._current_sort_reverse
        self._refresh_table()

    def _refresh_table(self) -> None:
        search_term = self._search_var.get().strip()
        if search_term:
            items = self._controller.search_items(search_term)
        else:
            items = self._controller.get_all_items()

        sort_key = self._current_sort_key
        reverse = self._current_sort_reverse
        if sort_key == "name":
            items = self._controller.get_sorted_by_name(reverse)
        elif sort_key == "price":
            items = self._controller.get_sorted_by_price(reverse)
        elif sort_key == "quantity" or sort_key == "category":
            items = self._controller.get_sorted_by_quantity(reverse) if sort_key == "quantity" \
                else self._controller.get_sorted_by_name(reverse)

        if search_term:
            items = self._controller.search_items(search_term)

        rows = []
        for item in items:
            rows.append([
                item.id, item.name, item.category, item.quantity,
                f"\u00a3{item.price:.2f}", item.min_stock_level,
                item.stock_status, f"\u00a3{item.total_value:.2f}",
            ])
        self._table.set_data(rows)

        self._update_low_stock()
        self._update_stats()

    def _update_low_stock(self) -> None:
        low_items = self._controller.get_low_stock_items()
        if low_items:
            text = "\u26a0\ufe0f  Low Stock Items:  " + ", ".join(
                f"{item.name} ({item.quantity}/{item.min_stock_level})"
                for item in low_items
            )
            self._low_stock_label.configure(text=text, text_color="#ff8c00")
        else:
            self._low_stock_label.configure(
                text="\u2705  All items have sufficient stock", text_color="#2d8a4e"
            )

    def _update_stats(self) -> None:
        total = self._controller.get_total_items()
        value = self._controller.get_total_value()
        categories = self._controller.get_category_summary()
        cats = ", ".join(f"{cat}: {info['count']}" for cat, info in categories.items())
        self._stats_label.configure(
            text=f"Total Items: {total}  |  Total Value: \u00a3{value:,.2f}  |  "
                 f"Categories: {cats}"
        )

    def _on_row_select(self, row_data: Optional) -> None:
        if row_data:
            self._edit_btn.configure(state="normal")
            self._delete_btn.configure(state="normal")
        else:
            self._edit_btn.configure(state="disabled")
            self._delete_btn.configure(state="disabled")

    def _show_add_dialog(self) -> None:
        InventoryItemDialog(self, title="Add Inventory Item",
                            on_save=self._on_add_save)

    def _on_add_save(self, data: Dict[str, Any]) -> None:
        try:
            self._controller.add_item(
                name=data["name"], category=data["category"],
                quantity=int(data["quantity"]), price=float(data["price"]),
                min_stock_level=int(data["min_stock"]), description=data["description"],
            )
            self._refresh_table()
            InfoDialog(self, "Success", "Item added successfully", "success")
        except (ValueError, Exception) as e:
            InfoDialog(self, "Error", str(e), "error")

    def _show_edit_dialog(self) -> None:
        selection = self._table.get_selected_row()
        if not selection:
            return
        _, values = selection
        item_id = int(values[0])
        item = self._controller.get_item(item_id)
        if item:
            InventoryItemDialog(
                self, title="Edit Inventory Item", item=item,
                on_save=lambda data: self._on_edit_save(item_id, data),
            )

    def _on_edit_save(self, item_id: int, data: Dict[str, Any]) -> None:
        try:
            self._controller.update_item(
                item_id=item_id, name=data["name"], category=data["category"],
                quantity=int(data["quantity"]), price=float(data["price"]),
                min_stock_level=int(data["min_stock"]), description=data["description"],
            )
            self._refresh_table()
            InfoDialog(self, "Success", "Item updated successfully", "success")
        except (ValueError, Exception) as e:
            InfoDialog(self, "Error", str(e), "error")

    def _confirm_delete(self) -> None:
        selection = self._table.get_selected_row()
        if not selection:
            return
        _, values = selection
        item_id = int(values[0])
        item_name = str(values[1])

        dialog = ConfirmDialog(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{item_name}'?"
        )
        self.wait_window(dialog)
        if dialog.get_result():
            self._controller.delete_item(item_id)
            self._refresh_table()
            InfoDialog(self, "Success", "Item deleted successfully", "success")

    def _import_sample(self) -> None:
        from utils.helpers import generate_sample_data
        try:
            samples = generate_sample_data()
            count = 0
            for item_data in samples["inventory"]:
                self._controller.add_item(**item_data)
                count += 1
            self._refresh_table()
            InfoDialog(self, "Success", f"{count} sample items imported", "success")
        except Exception as e:
            InfoDialog(self, "Error", f"Failed to import: {e}", "error")

    def action_new(self) -> None:
        self._show_add_dialog()

    def action_edit(self) -> None:
        if self._edit_btn.cget("state") != "disabled":
            self._show_edit_dialog()

    def action_delete(self) -> None:
        if self._delete_btn.cget("state") != "disabled":
            self._confirm_delete()

    def action_search(self) -> None:
        self._search_entry.focus_set()

    def action_run(self) -> None:
        self._show_report()

    def _show_report(self) -> None:
        report = self._controller.generate_report()
        text = (
            f"Inventory Report\n"
            f"{'=' * 50}\n"
            f"Total Items: {report['total_items']}\n"
            f"Total Value: \u00a3{report['total_value']:,.2f}\n"
            f"Low Stock Items: {report['low_stock_count']}\n\n"
            f"By Category:\n"
        )
        for cat, info in report["categories"].items():
            text += f"  \u2022 {cat}: {info['count']} items, \u00a3{info['total_value']:,.2f}\n"
        text += f"\nGenerated: {report['generated_at']}"

        dialog = InfoDialog(self, "Inventory Report", text, "info", width=500, height=400)


class InventoryItemDialog(ctk.CTkToplevel):
    """Dialog for adding/editing an inventory item."""

    def __init__(
        self, master, title: str, on_save,
        item: Optional[InventoryItem] = None,
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("480x520")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._on_save = on_save
        self._item = item

        self._center_on_parent(master)
        self._build_form()

    def _center_on_parent(self, master) -> None:
        self.update_idletasks()
        pw = master.winfo_width()
        ph = master.winfo_height()
        px = master.winfo_x()
        py = master.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_form(self) -> None:
        main = ctk.CTkScrollableFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        fields = [
            ("name", "Item Name", ctk.CTkEntry, {"placeholder_text": "Enter item name"}),
            ("category", "Category", ctk.CTkOptionMenu, {"values": ["Electronics", "Furniture", "Stationery", "General", "Other"]}),
            ("quantity", "Quantity", ctk.CTkEntry, {"placeholder_text": "Enter quantity"}),
            ("price", "Price (\u00a3)", ctk.CTkEntry, {"placeholder_text": "Enter price"}),
            ("min_stock", "Min Stock Level", ctk.CTkEntry, {"placeholder_text": "Enter minimum stock"}),
            ("description", "Description", ctk.CTkEntry, {"placeholder_text": "Enter description (optional)"}),
        ]

        self._entries = {}
        for key, label, widget_type, kwargs in fields:
            ctk.CTkLabel(main, text=label, font=ctk.CTkFont(size=13), anchor="w") \
                .pack(fill="x", pady=(8, 2))
            if widget_type == ctk.CTkOptionMenu:
                widget = widget_type(main, **kwargs)
            else:
                widget = widget_type(main, font=ctk.CTkFont(size=13), **kwargs)
            widget.pack(fill="x", pady=(0, 4))
            self._entries[key] = widget

        if self._item:
            self._entries["name"].insert(0, self._item.name)
            self._entries["category"].set(self._item.category)
            self._entries["quantity"].insert(0, str(self._item.quantity))
            self._entries["price"].insert(0, str(self._item.price))
            self._entries["min_stock"].insert(0, str(self._item.min_stock_level))
            self._entries["description"].insert(0, self._item.description)
        else:
            self._entries["category"].set("General")

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))

        ctk.CTkButton(
            btn_frame, text="Save", command=self._save,
            fg_color="#2d8a4e", hover_color="#236b3d",
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Cancel", command=self.destroy,
            fg_color="#555555",
            font=ctk.CTkFont(size=13),
        ).pack(side="left")

    def _save(self) -> None:
        data = {
            "name": self._entries["name"].get(),
            "category": self._entries["category"].get(),
            "quantity": self._entries["quantity"].get(),
            "price": self._entries["price"].get(),
            "min_stock": self._entries["min_stock"].get(),
            "description": self._entries["description"].get(),
        }
        try:
            self._on_save(data)
            self.destroy()
        except Exception as e:
            InfoDialog(self, "Validation Error", str(e), "error")
