from typing import Any, Dict, List

import customtkinter as ctk

from controllers.inventory_controller import InventoryController
from controllers.resource_controller import ResourceController
from controllers.scheduling_controller import SchedulingController
from views.components import CardFrame, MetricCard, SectionHeader


class DashboardView(ctk.CTkFrame):
    """Dashboard view displaying summary metrics and system status."""

    def __init__(
        self, master,
        inventory_ctrl: InventoryController,
        scheduling_ctrl: SchedulingController,
        resource_ctrl: ResourceController,
        nav_callback=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self._inventory_ctrl = inventory_ctrl
        self._scheduling_ctrl = scheduling_ctrl
        self._resource_ctrl = resource_ctrl
        self._nav_callback = nav_callback

        self._build_ui()

    def _build_ui(self) -> None:
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            scroll_frame, title="Dashboard",
            subtitle="Overview of the Algorithms & Data Structures Management Suite"
        ).pack(fill="x", pady=(0, 20))

        self._build_metrics_row(scroll_frame)

        self._build_algorithms_card(scroll_frame)

        self._build_quick_actions(scroll_frame)

    def _build_metrics_row(self, parent) -> None:
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 20))

        total_items = self._inventory_ctrl.get_total_items()
        total_value = self._inventory_ctrl.get_total_value()
        low_stock = self._inventory_ctrl.get_low_stock_count()
        total_bookings = self._scheduling_ctrl.get_total_bookings()
        conflicts = self._scheduling_ctrl.get_conflict_count()
        total_processes = self._resource_ctrl.get_process_count()

        self._total_items_card = MetricCard(
            metrics_frame, title="Total Inventory Items",
            value=str(total_items), subtitle="Items in stock",
            accent_color="#1f538d", width=200, height=130,
        )
        self._total_items_card.pack(side="left", padx=(0, 12), fill="x", expand=True)

        self._total_value_card = MetricCard(
            metrics_frame, title="Total Inventory Value",
            value=f"\u00a3{total_value:,.2f}", subtitle="Stock value",
            accent_color="#2d8a4e", width=200, height=130,
        )
        self._total_value_card.pack(side="left", padx=(0, 12), fill="x", expand=True)

        self._low_stock_card = MetricCard(
            metrics_frame, title="Low Stock Items",
            value=str(low_stock),
            subtitle="Requires attention",
            accent_color="#a83232" if low_stock > 0 else "#2d8a4e",
            width=200, height=130,
        )
        self._low_stock_card.pack(side="left", padx=(0, 12), fill="x", expand=True)

        self._bookings_card = MetricCard(
            metrics_frame, title="Active Bookings",
            value=str(total_bookings),
            subtitle=f"{conflicts} conflicts detected",
            accent_color="#b8860b" if conflicts > 0 else "#1f538d",
            width=200, height=130,
        )
        self._bookings_card.pack(side="left", padx=(0, 12), fill="x", expand=True)

        self._processes_card = MetricCard(
            metrics_frame, title="Processes",
            value=str(total_processes), subtitle="In scheduling queue",
            accent_color="#6a1f8d", width=200, height=130,
        )
        self._processes_card.pack(side="left", fill="x", expand=True)

    def _build_algorithms_card(self, parent) -> None:
        algo_frame = CardFrame(
            parent, title="Implemented Algorithms & Data Structures",
            width=0, height=200,
        )
        algo_frame.pack(fill="x", pady=(0, 20))

        left = ctk.CTkFrame(algo_frame.content, fg_color="transparent")
        right = ctk.CTkFrame(algo_frame.content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="left", fill="both", expand=True)

        algo_text_left = (
            "Search Algorithms:\n"
            "  \u2022 Linear Search (O(n))\n"
            "  \u2022 Binary Search (O(log n))\n\n"
            "Sorting Algorithms:\n"
            "  \u2022 Merge Sort (O(n log n))\n"
            "  \u2022 Quick Sort (O(n log n) avg)\n\n"
            "Data Structures:\n"
            "  \u2022 Dictionaries (hash-based)\n"
            "  \u2022 Lists / Arrays\n"
        )
        ctk.CTkLabel(
            left, text=algo_text_left, font=ctk.CTkFont(size=12),
            anchor="w", justify="left"
        ).pack(fill="both", expand=True)

        algo_text_right = (
            "CPU Scheduling Algorithms:\n"
            "  \u2022 First Come First Served\n"
            "  \u2022 Shortest Job First\n"
            "  \u2022 Round Robin\n"
            "  \u2022 Priority Scheduling\n\n"
            "Interval Algorithms:\n"
            "  \u2022 Overlap Detection (O(n log n))\n"
            "  \u2022 Available Slot Finding\n\n"
            "Data Structures:\n"
            "  \u2022 Queue / Priority Queue\n"
            "  \u2022 Collections / Intervals\n"
        )
        ctk.CTkLabel(
            right, text=algo_text_right, font=ctk.CTkFont(size=12),
            anchor="w", justify="left"
        ).pack(fill="both", expand=True)

    def _build_quick_actions(self, parent) -> None:
        actions_frame = CardFrame(
            parent, title="Quick Actions", width=0, height=120,
        )
        actions_frame.pack(fill="x")

        btn_frame = ctk.CTkFrame(actions_frame.content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=8)

        actions = [
            ("Inventory", "inventory"),
            ("Scheduling", "scheduling"),
            ("Resource Allocation", "resource"),
        ]
        for label, view_id in actions:
            btn = ctk.CTkButton(
                btn_frame, text=f"Open {label}",
                font=ctk.CTkFont(size=13),
                height=40, corner_radius=8,
                command=lambda vid=view_id: self._nav_callback(vid) if self._nav_callback else None,
            )
            btn.pack(side="left", padx=(0, 10), fill="x", expand=True)

    def refresh(self) -> None:
        total_items = self._inventory_ctrl.get_total_items()
        total_value = self._inventory_ctrl.get_total_value()
        low_stock = self._inventory_ctrl.get_low_stock_count()
        total_bookings = self._scheduling_ctrl.get_total_bookings()
        conflicts = self._scheduling_ctrl.get_conflict_count()
        total_processes = self._resource_ctrl.get_process_count()

        self._total_items_card.update_value(str(total_items))
        self._total_value_card.update_value(f"\u00a3{total_value:,.2f}")
        low_stock_color = "#a83232" if low_stock > 0 else "#2d8a4e"
        self._low_stock_card.update_value(str(low_stock))
        conflict_color = "#b8860b" if conflicts > 0 else "#1f538d"
        self._bookings_card.update_value(str(total_bookings))
        self._processes_card.update_value(str(total_processes))
