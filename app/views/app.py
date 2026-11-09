import json
from typing import Any, Dict, Optional

import customtkinter as ctk

from controllers.inventory_controller import InventoryController
from controllers.resource_controller import ResourceController
from controllers.scheduling_controller import SchedulingController
from utils.database import DatabaseManager
from utils.helpers import generate_sample_data
from utils.logger import LoggerSetup
from views.dashboard import DashboardView
from views.inventory_view import InventoryView
from views.scheduling_view import SchedulingView
from views.resource_view import ResourceView


logger = LoggerSetup.get_logger(__name__)


class App(ctk.CTk):
    """Main application window with sidebar navigation and module switching."""

    STATUS_KEYS = ["dashboard", "inventory", "scheduling", "resource"]

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self._config = config
        self._current_view_id = "dashboard"
        self._setup_window()
        self._setup_theme()

        self._db = DatabaseManager(config.get("database_path", "data/management_suite.db"))
        self._db.initialize_tables()

        self._inventory_ctrl = InventoryController(self._db)
        self._scheduling_ctrl = SchedulingController(self._db)
        self._resource_ctrl = ResourceController(self._db)

        self._load_sample_data_if_needed()

        self._views: Dict[str, ctk.CTkFrame] = {}
        self._nav_buttons: Dict[str, ctk.CTkButton] = {}
        self._status_label: Optional[ctk.CTkLabel] = None
        self._progress_bar: Optional[ctk.CTkProgressBar] = None

        self._build_sidebar()
        self._build_status_bar()
        self._build_main_area()
        self._show_view("dashboard")

        self._bind_shortcuts()

    def _setup_window(self) -> None:
        title = self._config.get("app_name", "Algorithms & Data Structures Management Suite")
        self.title(title)
        w = self._config.get("window_width", 1280)
        h = self._config.get("window_height", 800)
        self.geometry(f"{w}x{h}")
        self.minsize(
            self._config.get("min_window_width", 1024),
            self._config.get("min_window_height", 600),
        )
        self._center_window(w, h)

    def _center_window(self, w: int, h: int) -> None:
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    def _setup_theme(self) -> None:
        ctk.set_appearance_mode(self._config.get("appearance_mode", "dark"))
        ctk.set_default_color_theme(self._config.get("color_theme", "blue"))

    def show_progress(self, show: bool = True) -> None:
        if self._progress_bar:
            if show:
                self._progress_bar.pack(fill="x", before=self._status_bar)
                self._progress_bar.start()
            else:
                self._progress_bar.stop()
                self._progress_bar.pack_forget()
            self.update_idletasks()

    def set_status(self, text: str) -> None:
        if self._status_label:
            self._status_label.configure(text=text)
            self.update_idletasks()

    def _load_sample_data_if_needed(self) -> None:
        if not self._config.get("sample_data_on_first_run", True):
            return
        if self._inventory_ctrl.get_total_items() > 0:
            return

        try:
            samples = generate_sample_data()
            for item_data in samples["inventory"]:
                self._inventory_ctrl.add_item(**item_data)
            for booking_data in samples["bookings"]:
                self._scheduling_ctrl.book_resource(**booking_data)
            for proc_data in samples["processes"]:
                self._resource_ctrl.add_process(**proc_data)
            logger.info("Sample data loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load sample data: {e}")

    def load_sample_data(self) -> None:
        """Public method to manually load sample data from any view."""
        self._load_sample_data_if_needed()
        self.set_status("Sample data loaded")
        self._refresh_current()

    def _build_sidebar(self) -> None:
        self._sidebar = ctk.CTkFrame(
            self, width=self._config.get("sidebar_width", 220),
            corner_radius=0,
        )
        self._sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self._sidebar.pack_propagate(False)

        header_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(24, 24))

        ctk.CTkLabel(
            header_frame, text="",
            font=ctk.CTkFont(size=32),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame, text="Management\nSuite",
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        sep = ctk.CTkFrame(self._sidebar, height=2, fg_color="#333333")
        sep.pack(fill="x", padx=16, pady=(0, 16))

        nav_items = [
            ("dashboard", "", "Dashboard"),
            ("inventory", "", "Inventory"),
            ("scheduling", "", "Scheduling"),
            ("resource", "", "Resource Alloc."),
        ]

        for view_id, icon, label in nav_items:
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                height=44,
                corner_radius=8,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("#d0d0d0", "#333333"),
                command=lambda vid=view_id: self._show_view(vid),
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._nav_buttons[view_id] = btn

        sep2 = ctk.CTkFrame(self._sidebar, height=2, fg_color="#333333")
        sep2.pack(fill="x", padx=16, pady=(16, 16))

        ctk.CTkLabel(
            self._sidebar,
            text=f"v{self._config.get('version', '1.0.0')}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).pack(side="bottom", pady=16)

        ctk.CTkLabel(
            self._sidebar,
            text="Ctrl+F1  Help\nCtrl+Q  Quit",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        ).pack(side="bottom", pady=(0, 8))

    def _build_status_bar(self) -> None:
        self._status_bar = ctk.CTkFrame(self, height=28, corner_radius=0, fg_color="#1a1a2e")
        self._status_bar.pack(side="bottom", fill="x")
        self._progress_bar = ctk.CTkProgressBar(self._status_bar, height=3, mode="indeterminate")
        self._status_label = ctk.CTkLabel(
            self._status_bar, text="Ready | Dashboard",
            font=ctk.CTkFont(size=11), anchor="w",
            text_color="#aaaaaa",
        )
        self._status_label.pack(side="left", padx=12, pady=2, fill="x", expand=True)
        self._shortcuts_label = ctk.CTkLabel(
            self._status_bar,
            text="Ctrl+N: New  |  Ctrl+E: Edit  |  Ctrl+D: Delete  |  Ctrl+F: Search  |  F5: Refresh",
            font=ctk.CTkFont(size=10), anchor="e",
            text_color="#666666",
        )
        self._shortcuts_label.pack(side="right", padx=12)

    def _build_main_area(self) -> None:
        self._main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a2e")
        self._main_frame.pack(side="right", fill="both", expand=True)

        self._views["dashboard"] = DashboardView(
            self._main_frame, self._inventory_ctrl,
            self._scheduling_ctrl, self._resource_ctrl,
            nav_callback=self._show_view,
        )
        self._views["inventory"] = InventoryView(
            self._main_frame, self._inventory_ctrl,
        )
        self._views["scheduling"] = SchedulingView(
            self._main_frame, self._scheduling_ctrl,
        )
        self._views["resource"] = ResourceView(
            self._main_frame, self._resource_ctrl,
        )

        for view in self._views.values():
            view.pack(fill="both", expand=True)
            view.pack_forget()

    def _show_view(self, view_id: str) -> None:
        self._current_view_id = view_id
        for vid, view in self._views.items():
            if vid == view_id:
                view.pack(fill="both", expand=True)
                if hasattr(view, "refresh"):
                    view.refresh()
            else:
                view.pack_forget()

        for vid, btn in self._nav_buttons.items():
            if vid == view_id:
                btn.configure(fg_color=("#d0d0d0", "#2b2b2b"))
            else:
                btn.configure(fg_color="transparent")

        name_map = {"dashboard": "Dashboard", "inventory": "Inventory",
                    "scheduling": "Scheduling", "resource": "Resource Allocation"}
        self.set_status(f"Ready | {name_map.get(view_id, view_id)}")
        logger.info(f"Switched to view: {view_id}")

    def _get_current_view(self) -> Optional[Any]:
        for vid, view in self._views.items():
            if view.winfo_ismapped():
                return view
        return None

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-q>", lambda e: self.on_closing())
        self.bind("<Control-Q>", lambda e: self.on_closing())
        self.bind("<Control-n>", lambda e: self._dispatch("new"))
        self.bind("<Control-N>", lambda e: self._dispatch("new"))
        self.bind("<Control-e>", lambda e: self._dispatch("edit"))
        self.bind("<Control-E>", lambda e: self._dispatch("edit"))
        self.bind("<Control-d>", lambda e: self._dispatch("delete"))
        self.bind("<Control-D>", lambda e: self._dispatch("delete"))
        self.bind("<Control-f>", lambda e: self._dispatch("search"))
        self.bind("<Control-F>", lambda e: self._dispatch("search"))
        self.bind("<Control-r>", lambda e: self._dispatch("run"))
        self.bind("<Control-R>", lambda e: self._dispatch("run"))
        self.bind("<F5>", lambda e: self._refresh_current())
        self.bind("<F1>", lambda e: self._show_help())
        self.bind("<Control-F1>", lambda e: self._show_keyboard_shortcuts())

        for i, (vid, _, _) in enumerate([
            ("dashboard", "", ""), ("inventory", "", ""),
            ("scheduling", "", ""), ("resource", "", ""),
        ], start=1):
            key = f"<Alt-{i}>"
            self.bind(key, lambda e, v=vid: self._show_view(v))

    def _dispatch(self, action: str) -> None:
        view = self._get_current_view()
        if view and hasattr(view, f"action_{action}"):
            getattr(view, f"action_{action}")()

    def _refresh_current(self) -> None:
        view = self._get_current_view()
        if view and hasattr(view, "refresh"):
            view.refresh()
            self.set_status("Refreshed")

    def _show_help(self) -> None:
        from views.components import InfoDialog
        help_text = (
            "Algorithms & Data Structures Management Suite\n\n"
            "Three integrated modules:\n"
            "  1. Inventory Management - CRUD, search, sort, low-stock\n"
            "  2. Resource Scheduling - Book resources, conflict detection\n"
            "  3. Resource Allocation - CPU scheduling algorithms\n\n"
            "Navigate using the sidebar or Alt+1 through Alt+4.\n"
            "Press Ctrl+F1 for keyboard shortcuts."
        )
        InfoDialog(self, "Help", help_text, "info", width=450, height=300)

    def _show_keyboard_shortcuts(self) -> None:
        from views.components import InfoDialog
        shortcuts = (
            "Keyboard Shortcuts:\n\n"
            "  Ctrl+N     New item / booking / process\n"
            "  Ctrl+E     Edit selected item\n"
            "  Ctrl+D     Delete selected item\n"
            "  Ctrl+F     Focus search bar\n"
            "  Ctrl+R     Run algorithm (Resource view)\n"
            "  F5         Refresh current view\n"
            "  F1         Help\n"
            "  Ctrl+F1    This shortcut list\n"
            "  Ctrl+Q     Quit application\n"
            "  Alt+1-4    Switch views (Dashboard=1, Inventory=2,\n"
            "             Scheduling=3, Resource=4)"
        )
        InfoDialog(self, "Keyboard Shortcuts", shortcuts, "info", width=450, height=350)

    def on_closing(self) -> None:
        self._db.disconnect()
        self.destroy()
