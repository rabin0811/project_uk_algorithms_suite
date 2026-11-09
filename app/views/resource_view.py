from typing import Any, Dict, List, Optional

import customtkinter as ctk

from controllers.resource_controller import ResourceController
from models.resource_allocation import Process
from views.components import (
    CardFrame,
    ComplexityCard,
    ConfirmDialog,
    InfoDialog,
    SectionHeader,
    TableView,
    Tooltip,
)


class ResourceView(ctk.CTkFrame):
    """Resource allocation view with CPU scheduling algorithm visualization."""

    def __init__(self, master, controller: ResourceController, **kwargs):
        super().__init__(master, **kwargs)
        self._controller = controller
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        self._scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll_frame.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            self._scroll_frame, title="Dynamic Resource Allocation",
            subtitle="CPU Scheduling Algorithms: FCFS, SJF, Round Robin, Priority"
        ).pack(fill="x", pady=(0, 20))

        self._build_toolbar()
        self._build_table()
        self._build_queue_visualization()
        self._build_scheduling_controls()
        self._build_results_frame()
        self._build_complexity()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        left = ctk.CTkFrame(toolbar, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        self._add_btn = ctk.CTkButton(
            left, text="+  Add Process", width=130,
            command=self._show_add_dialog,
            font=ctk.CTkFont(size=13), fg_color="#2d8a4e", hover_color="#236b3d",
        )
        self._add_btn.pack(side="left", padx=(0, 8))
        Tooltip(self._add_btn, "Add a new process to the scheduling queue")

        self._remove_btn = ctk.CTkButton(
            left, text="Remove Selected", width=130,
            command=self._confirm_remove, state="disabled",
            font=ctk.CTkFont(size=12), fg_color="#a83232", hover_color="#8a2828",
        )
        self._remove_btn.pack(side="left", padx=(0, 8))

        self._clear_btn = ctk.CTkButton(
            left, text="Clear Completed", width=130,
            command=self._confirm_clear_completed,
            font=ctk.CTkFont(size=12), fg_color="#555555",
        )
        self._clear_btn.pack(side="left", padx=(0, 8))
        Tooltip(self._clear_btn, "Remove all completed processes")

        self._history_btn = ctk.CTkButton(
            left, text="Process History", width=130,
            command=self._show_process_history,
            font=ctk.CTkFont(size=12), fg_color="#6a1f8d", hover_color="#551a73",
        )
        self._history_btn.pack(side="left", padx=(0, 8))
        Tooltip(self._history_btn, "View completed process history")

    def _build_table(self) -> None:
        self._table_frame = CardFrame(
            self._scroll_frame, title="Process Queue", width=0, height=280,
        )
        self._table_frame.pack(fill="x", pady=(0, 12))

        columns = ["ID", "Name", "Burst Time", "Priority", "Arrival Time",
                    "Status", "Remaining"]
        widths = [50, 160, 100, 80, 100, 100, 100]
        self._table = TableView(
            self._table_frame.content, columns=columns, column_widths=widths,
            height=200,
        )
        self._table.pack(fill="both", expand=True)
        self._table.on_select(self._on_row_select)

        btn_frame = ctk.CTkFrame(self._table_frame.content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 0))

        self._quantum_label = ctk.CTkLabel(
            btn_frame, text="Time Quantum:", font=ctk.CTkFont(size=12),
        )
        self._quantum_label.pack(side="left", padx=(0, 4))

        self._quantum_var = ctk.StringVar(value="4")
        self._quantum_entry = ctk.CTkEntry(
            btn_frame, textvariable=self._quantum_var, width=60,
            font=ctk.CTkFont(size=12),
        )
        self._quantum_entry.pack(side="left", padx=(0, 8))
        Tooltip(self._quantum_entry, "Time quantum for Round Robin (default: 4)")

    def _build_queue_visualization(self) -> None:
        self._viz_frame = CardFrame(
            self._scroll_frame, title="Queue Visualization", width=0, height=120,
        )
        self._viz_frame.pack(fill="x", pady=(0, 12))
        self._viz_progress = ctk.CTkProgressBar(
            self._viz_frame.content, height=6, mode="determinate",
        )
        self._viz_progress.pack(fill="x", padx=8, pady=(8, 4))
        self._viz_progress.set(0)
        self._viz_label = ctk.CTkLabel(
            self._viz_frame.content, text="Waiting Queue: [empty]",
            font=ctk.CTkFont(size=13), anchor="w",
        )
        self._viz_label.pack(fill="x", padx=8, pady=(0, 8))

    def _build_scheduling_controls(self) -> None:
        controls_frame = CardFrame(
            self._scroll_frame, title="Scheduling Algorithms", width=0, height=160,
        )
        controls_frame.pack(fill="x", pady=(0, 12))

        label = ctk.CTkLabel(
            controls_frame.content, text="Select an algorithm to simulate:",
            font=ctk.CTkFont(size=13),
        )
        label.pack(anchor="w", pady=(0, 8))

        algo_frame = ctk.CTkFrame(controls_frame.content, fg_color="transparent")
        algo_frame.pack(fill="x")

        algorithms = [
            ("FCFS", self._run_fcfs, "#1f538d"),
            ("SJF", self._run_sjf, "#2d8a4e"),
            ("Round Robin", self._run_rr, "#b8860b"),
            ("Priority", self._run_priority, "#6a1f8d"),
        ]

        for algo_name, command, color in algorithms:
            btn = ctk.CTkButton(
                algo_frame, text=algo_name, command=command,
                width=140, height=36,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=color, hover_color=color,
            )
            btn.pack(side="left", padx=(0, 10))
            Tooltip(btn, f"Run {algo_name} scheduling algorithm")

    def _build_complexity(self) -> None:
        algo_info = [
            {"name": "FCFS", "time": "O(n log n)", "space": "O(n)"},
            {"name": "SJF", "time": "O(n^2)", "space": "O(n)"},
            {"name": "Round Robin", "time": "O(n)", "space": "O(n)"},
            {"name": "Priority", "time": "O(n^2)", "space": "O(n)"},
            {"name": "MinHeap", "time": "O(log n)", "space": "O(n)"},
        ]
        self._complexity_card = ComplexityCard(
            self._scroll_frame, complexities=algo_info,
        )
        self._complexity_card.pack(fill="x", pady=(12, 0))

    def _build_results_frame(self) -> None:
        self._results_frame = CardFrame(
            self._scroll_frame, title="Algorithm Results", width=0, height=250,
        )
        self._results_frame.pack(fill="x")

        self._results_text = ctk.CTkTextbox(
            self._results_frame.content, font=ctk.CTkFont(size=12),
            state="disabled", height=160,
        )
        self._results_text.pack(fill="both", expand=True)

    def _refresh_table(self) -> None:
        processes = self._controller.get_all_processes()
        rows = []
        for p in processes:
            rows.append([
                p.id, p.name, p.burst_time, p.priority,
                p.arrival_time, p.status, p.remaining_time,
            ])
        self._table.set_data(rows)
        self._update_queue_viz()

    def _update_queue_viz(self) -> None:
        pending = self._controller.get_pending_processes()
        if not pending:
            self._viz_label.configure(text="Waiting Queue: [empty]")
        else:
            names = " \u2192 ".join(p.name for p in pending[:8])
            if len(pending) > 8:
                names += f" ... (+{len(pending) - 8} more)"
            self._viz_label.configure(text=f"Waiting Queue: [{names}]")

    def _on_row_select(self, row_data: Optional) -> None:
        self._remove_btn.configure(
            state="normal" if row_data else "disabled"
        )

    def _show_add_dialog(self) -> None:
        ProcessDialog(self, title="Add Process", on_save=self._on_add_save)

    def _on_add_save(self, data: Dict[str, Any]) -> None:
        try:
            self._controller.add_process(
                name=data["name"], burst_time=int(data["burst_time"]),
                priority=int(data["priority"]), arrival_time=int(data["arrival_time"]),
            )
            self._refresh_table()
            InfoDialog(self, "Success", "Process added successfully", "success")
        except (ValueError, Exception) as e:
            InfoDialog(self, "Error", str(e), "error")

    def _confirm_remove(self) -> None:
        selection = self._table.get_selected_row()
        if not selection:
            return
        _, values = selection
        proc_id = int(values[0])

        dialog = ConfirmDialog(
            self, "Remove Process",
            "Are you sure you want to remove this process?"
        )
        self.wait_window(dialog)
        if dialog.get_result():
            self._controller.remove_process(proc_id)
            self._refresh_table()
            InfoDialog(self, "Success", "Process removed", "success")

    def _confirm_clear_completed(self) -> None:
        dialog = ConfirmDialog(
            self, "Clear Completed",
            "Remove all completed processes from the queue?"
        )
        self.wait_window(dialog)
        if dialog.get_result():
            self._controller.clear_completed()
            self._refresh_table()
            InfoDialog(self, "Success", "Completed processes cleared", "success")

    def _show_process_history(self) -> None:
        completed = self._controller.get_completed_processes()
        if not completed:
            InfoDialog(self, "Process History", "No completed processes found", "info")
            return
        text = "Completed Process History:\n"
        text += f"{'='*50}\n\n"
        text += f"{'Name':<15} {'Burst':<8} {'Priority':<10} {'Wait':<8} {'Turnaround':<12}\n"
        text += "-"*50 + "\n"
        for p in completed:
            text += f"{p.name:<15} {p.burst_time:<8} {p.priority:<10} "
            text += f"{p.waiting_time:<8} {p.turnaround_time:<12}\n"
        self._results_text.configure(state="normal")
        self._results_text.delete("0.0", "end")
        self._results_text.insert("0.0", text)
        self._results_text.configure(state="disabled")
        InfoDialog(self, "Process History", f"Showing {len(completed)} completed processes", "info")

    def action_new(self) -> None:
        self._show_add_dialog()

    def action_edit(self) -> None:
        pass

    def action_delete(self) -> None:
        if self._remove_btn.cget("state") != "disabled":
            self._confirm_remove()

    def action_search(self) -> None:
        pass

    def action_run(self) -> None:
        if self._controller.get_process_count() > 0:
            self._run_fcfs()

    def _display_results(self, algo_name: str, result: Dict[str, Any]) -> None:
        schedule = result["schedule"]
        avg_wait = result["avg_waiting_time"]
        avg_turn = result["avg_turnaround_time"]

        text = f"{algo_name} Scheduling Results:\n"
        text += f"{'=' * 50}\n\n"
        text += f"{'Process':<15} {'Start':<8} {'End':<8} {'Wait':<8} {'Turnaround':<12}\n"
        text += "-" * 50 + "\n"

        for entry in schedule:
            proc = entry["process"]
            text += f"{proc.name:<15} {entry['start']:<8} {entry['end']:<8} "
            text += f"{entry['waiting_time']:<8} {entry['turnaround_time']:<12}\n"

        text += f"\nAverage Waiting Time: {avg_wait}\n"
        text += f"Average Turnaround Time: {avg_turn}\n"
        text += f"Total Processes: {len(schedule)}"

        self._results_text.configure(state="normal")
        self._results_text.delete("0.0", "end")
        self._results_text.insert("0.0", text)
        self._results_text.configure(state="disabled")

    def _run_fcfs(self) -> None:
        result = self._controller.run_fcfs()
        self._display_results("FCFS (First Come First Served)", result)

    def _run_sjf(self) -> None:
        result = self._controller.run_sjf()
        self._display_results("SJF (Shortest Job First)", result)

    def _run_rr(self) -> None:
        try:
            quantum = int(self._quantum_var.get())
            if quantum <= 0:
                raise ValueError
        except ValueError:
            InfoDialog(self, "Error", "Time quantum must be a positive integer", "error")
            return
        result = self._controller.run_round_robin(quantum)
        self._display_results(f"Round Robin (q={quantum})", result)

    def _run_priority(self) -> None:
        result = self._controller.run_priority()
        self._display_results("Priority Scheduling", result)


class ProcessDialog(ctk.CTkToplevel):
    """Dialog for adding a process."""

    def __init__(self, master, title: str, on_save):
        super().__init__(master)
        self.title(title)
        self.geometry("400x380")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._on_save = on_save

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
            ("name", "Process Name", {"placeholder_text": "e.g. Data Processing A"}),
            ("burst_time", "Burst Time (CPU cycles)", {"placeholder_text": "e.g. 6"}),
            ("priority", "Priority (1 = highest)", {"placeholder_text": "e.g. 1"}),
            ("arrival_time", "Arrival Time", {"placeholder_text": "e.g. 0"}),
        ]

        self._entries = {}
        for key, label, kwargs in fields:
            ctk.CTkLabel(main, text=label, font=ctk.CTkFont(size=13), anchor="w") \
                .pack(fill="x", pady=(8, 2))
            widget = ctk.CTkEntry(main, font=ctk.CTkFont(size=13), **kwargs)
            widget.pack(fill="x", pady=(0, 4))
            self._entries[key] = widget

        self._entries["priority"].insert(0, "1")
        self._entries["arrival_time"].insert(0, "0")

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))

        ctk.CTkButton(
            btn_frame, text="Add Process", command=self._save,
            fg_color="#2d8a4e", hover_color="#236b3d",
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Cancel", command=self.destroy,
            fg_color="#555555", font=ctk.CTkFont(size=13),
        ).pack(side="left")

    def _save(self) -> None:
        data = {
            "name": self._entries["name"].get(),
            "burst_time": self._entries["burst_time"].get(),
            "priority": self._entries["priority"].get(),
            "arrival_time": self._entries["arrival_time"].get(),
        }
        try:
            self._on_save(data)
            self.destroy()
        except Exception as e:
            InfoDialog(self, "Validation Error", str(e), "error")
