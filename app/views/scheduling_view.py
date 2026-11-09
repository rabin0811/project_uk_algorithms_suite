from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import customtkinter as ctk

from controllers.scheduling_controller import SchedulingController
from models.scheduling import Booking
from views.components import (
    CardFrame,
    ComplexityCard,
    ConfirmDialog,
    InfoDialog,
    SectionHeader,
    TableView,
    Tooltip,
)


class SchedulingView(ctk.CTkFrame):
    """Resource scheduling view with booking management and conflict detection."""

    def __init__(self, master, controller: SchedulingController, **kwargs):
        super().__init__(master, **kwargs)
        self._controller = controller
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        self._scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll_frame.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            self._scroll_frame, title="Resource Scheduling",
            subtitle="Book, manage and detect conflicts for shared resources"
        ).pack(fill="x", pady=(0, 20))

        self._build_toolbar()
        self._build_table()
        self._build_conflicts_frame()
        self._build_schedule_view()
        self._build_complexity()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        left = ctk.CTkFrame(toolbar, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        self._search_var = ctk.StringVar()
        self._search_var.trace("w", lambda *a: self._refresh_table())
        self._search_entry = ctk.CTkEntry(
            left, placeholder_text="Search bookings...", width=250,
            font=ctk.CTkFont(size=13),
            textvariable=self._search_var,
        )
        self._search_entry.pack(side="left", padx=(0, 8))
        Tooltip(self._search_entry, "Search by resource, booker, or purpose")

        self._binary_search_btn = ctk.CTkButton(
            left, text="Binary Search", width=110,
            command=self._do_binary_search,
            font=ctk.CTkFont(size=11), fg_color="#1f538d",
        )
        self._binary_search_btn.pack(side="left", padx=(0, 8))
        Tooltip(self._binary_search_btn, "Binary search on sorted bookings (O(log n))")

        self._history_btn = ctk.CTkButton(
            left, text="Booking History", width=120,
            command=self._show_booking_history,
            font=ctk.CTkFont(size=11), fg_color="#555555",
        )
        self._history_btn.pack(side="left")
        Tooltip(self._history_btn, "View past booking history")

        right = ctk.CTkFrame(toolbar, fg_color="transparent")
        right.pack(side="right")

        self._add_btn = ctk.CTkButton(
            right, text="+  New Booking", width=130,
            command=self._show_add_dialog,
            font=ctk.CTkFont(size=13), fg_color="#2d8a4e", hover_color="#236b3d",
        )
        self._add_btn.pack(side="left", padx=(0, 8))
        Tooltip(self._add_btn, "Create a new resource booking")

        self._check_conflicts_btn = ctk.CTkButton(
            right, text="Check Conflicts", width=130,
            command=self._show_conflicts,
            font=ctk.CTkFont(size=13), fg_color="#b8860b", hover_color="#9a7209",
        )
        self._check_conflicts_btn.pack(side="left")
        Tooltip(self._check_conflicts_btn, "Detect all overlapping bookings")

    def _build_table(self) -> None:
        self._table_frame = CardFrame(
            self._scroll_frame, title="All Bookings", width=0, height=350,
        )
        self._table_frame.pack(fill="x", pady=(0, 12))

        columns = ["ID", "Resource", "Booker", "Start Time", "End Time",
                    "Duration (min)", "Purpose"]
        widths = [50, 150, 130, 160, 160, 100, 200]
        self._table = TableView(
            self._table_frame.content, columns=columns, column_widths=widths,
            height=280,
        )
        self._table.pack(fill="both", expand=True)
        self._table.on_select(self._on_row_select)

        btn_frame = ctk.CTkFrame(self._table_frame.content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 0))

        self._edit_btn = ctk.CTkButton(
            btn_frame, text="Edit Booking", width=120,
            command=self._show_edit_dialog, state="disabled",
            font=ctk.CTkFont(size=12),
        )
        self._edit_btn.pack(side="left", padx=(0, 8))

        self._delete_btn = ctk.CTkButton(
            btn_frame, text="Cancel Booking", width=120,
            command=self._confirm_delete, state="disabled",
            font=ctk.CTkFont(size=12), fg_color="#a83232", hover_color="#8a2828",
        )
        self._delete_btn.pack(side="left")

    def _build_conflicts_frame(self) -> None:
        self._conflicts_frame = CardFrame(
            self._scroll_frame, title="Conflict Detection Status", width=0, height=60,
        )
        self._conflicts_frame.pack(fill="x", pady=(0, 12))
        self._conflicts_label = ctk.CTkLabel(
            self._conflicts_frame.content, text="",
            font=ctk.CTkFont(size=13), anchor="w",
        )
        self._conflicts_label.pack(fill="x", padx=8, pady=8)

    def _build_complexity(self) -> None:
        algo_info = [
            {"name": "Interval Overlap", "time": "O(n log n)", "space": "O(n)"},
            {"name": "Binary Search", "time": "O(log n)", "space": "O(1)"},
            {"name": "Sorting (Merge)", "time": "O(n log n)", "space": "O(n)"},
        ]
        self._complexity_card = ComplexityCard(
            self._scroll_frame, complexities=algo_info,
        )
        self._complexity_card.pack(fill="x", pady=(12, 0))

    def _build_schedule_view(self) -> None:
        schedule_frame = CardFrame(
            self._scroll_frame, title="Daily Schedule View", width=0, height=200,
        )
        schedule_frame.pack(fill="x")

        controls = ctk.CTkFrame(schedule_frame.content, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 8))

        self._date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self._date_entry = ctk.CTkEntry(
            controls, textvariable=self._date_var, width=150,
            font=ctk.CTkFont(size=13),
        )
        self._date_entry.pack(side="left", padx=(0, 8))
        Tooltip(self._date_entry, "Enter date (YYYY-MM-DD)")

        ctk.CTkButton(
            controls, text="View Schedule", width=120,
            command=self._show_daily_schedule,
            font=ctk.CTkFont(size=12),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            controls, text="Available Slots", width=120,
            command=self._show_available_slots,
            font=ctk.CTkFont(size=12), fg_color="#6a1f8d", hover_color="#551a73",
        ).pack(side="left")

        self._schedule_text = ctk.CTkTextbox(
            schedule_frame.content, height=80, font=ctk.CTkFont(size=12),
            state="disabled",
        )
        self._schedule_text.pack(fill="both", expand=True)

    def _refresh_table(self) -> None:
        search_term = self._search_var.get().strip()
        if search_term:
            bookings = self._controller.search_bookings(search_term)
        else:
            bookings = self._controller.get_all_bookings()

        rows = []
        for b in bookings:
            rows.append([
                b.id, b.resource_name, b.booker_name,
                b.start_time[:19], b.end_time[:19],
                b.duration_minutes, b.purpose,
            ])
        self._table.set_data(rows)

        conflicts = self._controller.detect_all_conflicts()
        if conflicts:
            self._conflicts_label.configure(
                text=f"\u26a0\ufe0f  {len(conflicts)} scheduling conflict(s) detected. "
                     f"Click 'Check Conflicts' for details.",
                text_color="#ff8c00",
            )
        else:
            self._conflicts_label.configure(
                text="\u2705  No scheduling conflicts detected", text_color="#2d8a4e"
            )

    def _on_row_select(self, row_data: Optional) -> None:
        if row_data:
            self._edit_btn.configure(state="normal")
            self._delete_btn.configure(state="normal")
        else:
            self._edit_btn.configure(state="disabled")
            self._delete_btn.configure(state="disabled")

    def _do_binary_search(self) -> None:
        term = self._search_var.get().strip()
        if not term:
            InfoDialog(self, "Binary Search", "Enter a resource name first", "info")
            return
        sorted_bookings = self._controller.get_all_bookings()
        sorted_bookings.sort(key=lambda b: b.resource_name.lower())
        from algorithms.search import binary_search
        from models.inventory import InventoryItem
        result = None
        low, high = 0, len(sorted_bookings) - 1
        target_lower = term.lower()
        while low <= high:
            mid = (low + high) // 2
            mid_name = sorted_bookings[mid].resource_name.lower()
            if mid_name == target_lower:
                result = sorted_bookings[mid]
                break
            elif mid_name < target_lower:
                low = mid + 1
            else:
                high = mid - 1
        if result:
            rows = [[result.id, result.resource_name, result.booker_name,
                     result.start_time[:19], result.end_time[:19],
                     result.duration_minutes, result.purpose]]
            self._table.set_data(rows)
            InfoDialog(self, "Binary Search", f"Found: {result.resource_name} booked by {result.booker_name}", "success")
        else:
            InfoDialog(self, "Binary Search", f"No booking found for '{term}'", "info")

    def _show_booking_history(self) -> None:
        bookings = self._controller.get_all_bookings()
        now = datetime.now()
        past = [b for b in bookings if b.end_datetime < now]
        past.sort(key=lambda b: b.start_datetime, reverse=True)
        if not past:
            InfoDialog(self, "Booking History", "No past bookings found", "info")
            return
        rows = []
        for b in past:
            rows.append([b.id, b.resource_name, b.booker_name,
                         b.start_time[:16], b.end_time[:16], b.duration_minutes, b.purpose])
        self._table.set_data(rows)
        InfoDialog(self, "Booking History", f"Showing {len(past)} past bookings", "info")

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
        self._show_conflicts()

    def _show_add_dialog(self) -> None:
        BookingDialog(self, title="New Booking", on_save=self._on_add_save)

    def _on_add_save(self, data: Dict[str, Any]) -> None:
        try:
            booking, conflicts = self._controller.book_resource(
                resource_name=data["resource"], booker_name=data["booker"],
                start_time=data["start_time"], end_time=data["end_time"],
                purpose=data["purpose"],
            )
            if booking:
                self._refresh_table()
                InfoDialog(self, "Success", "Booking created successfully", "success")
            else:
                conflict_msg = "\n".join(
                    f"  \u2022 {c.booker_name} ({c.start_time[:16]} - {c.end_time[:16]})"
                    for c in conflicts
                )
                InfoDialog(
                    self, "Conflict Detected",
                    f"Cannot book - conflicts with:\n{conflict_msg}",
                    "warning",
                )
        except (ValueError, Exception) as e:
            InfoDialog(self, "Error", str(e), "error")

    def _show_edit_dialog(self) -> None:
        selection = self._table.get_selected_row()
        if not selection:
            return
        _, values = selection
        booking_id = int(values[0])
        booking = self._controller.get_booking(booking_id)
        if booking:
            BookingDialog(
                self, title="Edit Booking", booking=booking,
                on_save=lambda data: self._on_edit_save(booking_id, data),
            )

    def _on_edit_save(self, booking_id: int, data: Dict[str, Any]) -> None:
        try:
            booking, conflicts = self._controller.update_booking(
                booking_id=booking_id, resource_name=data["resource"],
                booker_name=data["booker"], start_time=data["start_time"],
                end_time=data["end_time"], purpose=data["purpose"],
            )
            if booking:
                self._refresh_table()
                InfoDialog(self, "Success", "Booking updated successfully", "success")
            else:
                conflict_msg = "\n".join(
                    f"  \u2022 {c.booker_name} ({c.start_time[:16]} - {c.end_time[:16]})"
                    for c in conflicts
                )
                InfoDialog(self, "Conflict Detected", conflict_msg, "warning")
        except (ValueError, Exception) as e:
            InfoDialog(self, "Error", str(e), "error")

    def _confirm_delete(self) -> None:
        selection = self._table.get_selected_row()
        if not selection:
            return
        _, values = selection
        booking_id = int(values[0])

        dialog = ConfirmDialog(
            self, "Cancel Booking",
            f"Are you sure you want to cancel this booking?"
        )
        self.wait_window(dialog)
        if dialog.get_result():
            self._controller.delete_booking(booking_id)
            self._refresh_table()
            InfoDialog(self, "Success", "Booking cancelled", "success")

    def _show_conflicts(self) -> None:
        conflicts = self._controller.detect_all_conflicts()
        if not conflicts:
            InfoDialog(self, "No Conflicts",
                       "No scheduling conflicts found.", "success")
            return

        msg = f"Found {len(conflicts)} conflict(s):\n\n"
        for b1, b2 in conflicts:
            msg += (
                f"\u26a0\ufe0f  {b1.resource_name}\n"
                f"  {b1.booker_name} ({b1.start_time[:16]}-{b1.end_time[:16]})\n"
                f"  vs {b2.booker_name} ({b2.start_time[:16]}-{b2.end_time[:16]})\n\n"
            )
        InfoDialog(self, "Scheduling Conflicts", msg, "warning", width=500, height=400)

    def _show_daily_schedule(self) -> None:
        date_str = self._date_var.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            InfoDialog(self, "Error", "Invalid date format. Use YYYY-MM-DD.", "error")
            return

        bookings = self._controller.get_bookings_for_date(date_str)
        if not bookings:
            text = f"No bookings scheduled for {date_str}"
        else:
            text = f"Schedule for {date_str}:\n"
            for b in bookings:
                text += f"  \u2022 {b.start_time[11:16]} - {b.end_time[11:16]}: "
                text += f"{b.resource_name} (Booked by {b.booker_name})\n"

        self._schedule_text.configure(state="normal")
        self._schedule_text.delete("0.0", "end")
        self._schedule_text.insert("0.0", text)
        self._schedule_text.configure(state="disabled")

    def _show_available_slots(self) -> None:
        date_str = self._date_var.get().strip()
        SlotFinderDialog(self, self._controller, date_str)


class BookingDialog(ctk.CTkToplevel):
    """Dialog for creating or editing a booking."""

    def __init__(
        self, master, title: str, on_save,
        booking: Optional[Booking] = None,
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("480x480")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._on_save = on_save
        self._booking = booking

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
            ("resource", "Resource Name", ctk.CTkEntry,
             {"placeholder_text": "e.g. Conference Room A"}),
            ("booker", "Booker Name", ctk.CTkEntry,
             {"placeholder_text": "e.g. Dr. Smith"}),
            ("start_time", "Start Time (YYYY-MM-DD HH:MM)", ctk.CTkEntry,
             {"placeholder_text": "e.g. 2026-07-22 09:00"}),
            ("end_time", "End Time (YYYY-MM-DD HH:MM)", ctk.CTkEntry,
             {"placeholder_text": "e.g. 2026-07-22 10:00"}),
            ("purpose", "Purpose (optional)", ctk.CTkEntry,
             {"placeholder_text": "e.g. Department Meeting"}),
        ]

        self._entries = {}
        for key, label, widget_type, kwargs in fields:
            ctk.CTkLabel(main, text=label, font=ctk.CTkFont(size=13), anchor="w") \
                .pack(fill="x", pady=(8, 2))
            widget = widget_type(main, font=ctk.CTkFont(size=13), **kwargs)
            widget.pack(fill="x", pady=(0, 4))
            self._entries[key] = widget

        if self._booking:
            self._entries["resource"].insert(0, self._booking.resource_name)
            self._entries["booker"].insert(0, self._booking.booker_name)
            self._entries["start_time"].insert(0, self._booking.start_time[:16])
            self._entries["end_time"].insert(0, self._booking.end_time[:16])
            self._entries["purpose"].insert(0, self._booking.purpose)

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))

        ctk.CTkButton(
            btn_frame, text="Save", command=self._save,
            fg_color="#2d8a4e", hover_color="#236b3d",
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Cancel", command=self.destroy,
            fg_color="#555555", font=ctk.CTkFont(size=13),
        ).pack(side="left")

    def _save(self) -> None:
        data = {
            "resource": self._entries["resource"].get(),
            "booker": self._entries["booker"].get(),
            "start_time": self._entries["start_time"].get(),
            "end_time": self._entries["end_time"].get(),
            "purpose": self._entries["purpose"].get(),
        }
        try:
            self._on_save(data)
            self.destroy()
        except Exception as e:
            InfoDialog(self, "Validation Error", str(e), "error")


class SlotFinderDialog(ctk.CTkToplevel):
    """Dialog to find and display available time slots."""

    def __init__(self, master, controller: SchedulingController, date_str: str):
        super().__init__(master)
        self.title("Available Time Slots")
        self.geometry("500x400")
        self.transient(master)
        self.grab_set()
        self._controller = controller
        self._date_str = date_str

        self._center_on_parent(master)
        self._build_ui()

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

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self, text=f"Available Slots for {self._date_str}",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(16, 8))

        resource_frame = ctk.CTkFrame(self, fg_color="transparent")
        resource_frame.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(
            resource_frame, text="Resource:",
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=(0, 8))

        self._resource_entry = ctk.CTkEntry(
            resource_frame, placeholder_text="e.g. Conference Room A",
            font=ctk.CTkFont(size=13), width=200,
        )
        self._resource_entry.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            resource_frame, text="Find Slots", command=self._find_slots,
            font=ctk.CTkFont(size=12),
        ).pack(side="left")

        self._results_text = ctk.CTkTextbox(
            self, font=ctk.CTkFont(size=12), state="disabled",
        )
        self._results_text.pack(fill="both", expand=True, padx=20, pady=(8, 16))

    def _find_slots(self) -> None:
        resource = self._resource_entry.get().strip()
        if not resource:
            InfoDialog(self, "Error", "Please enter a resource name", "error")
            return

        try:
            slots = self._controller.find_available_slots(resource, self._date_str)
        except Exception as e:
            InfoDialog(self, "Error", str(e), "error")
            return

        self._results_text.configure(state="normal")
        self._results_text.delete("0.0", "end")

        if not slots:
            self._results_text.insert("0.0", "No available slots found for this date.")
        else:
            text = f"Available 30-min slots for '{resource}' on {self._date_str}:\n\n"
            for start, end in slots:
                s = start[11:16] if "T" in start else start
                e = end[11:16] if "T" in end else end
                text += f"  \u2022 {s} - {e}\n"
            self._results_text.insert("0.0", text)

        self._results_text.configure(state="disabled")
