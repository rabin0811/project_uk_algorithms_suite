from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

import customtkinter as ctk


class CardFrame(ctk.CTkFrame):
    """A styled card frame with rounded corners and optional title."""

    def __init__(
        self, master, title: str = "", width: int = 280, height: int = 160,
        **kwargs
    ):
        super().__init__(master, width=width, height=height, **kwargs)
        self.configure(corner_radius=12)
        self.pack_propagate(False)

        if title:
            self._title_label = ctk.CTkLabel(
                self, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            self._title_label.pack(padx=16, pady=(12, 4), fill="x")

        self._content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._content_frame.pack(padx=16, pady=(0, 12), fill="both", expand=True)

    @property
    def content(self) -> ctk.CTkFrame:
        return self._content_frame


class MetricCard(CardFrame):
    """A card that displays a single metric with label and value."""

    def __init__(
        self, master, title: str, value: str,
        subtitle: str = "", accent_color: str = "#1f538d", **kwargs
    ):
        super().__init__(master, title="", **kwargs)
        self._accent_frame = ctk.CTkFrame(
            self, height=4, fg_color=accent_color, corner_radius=0
        )
        self._accent_frame.pack(fill="x", side="bottom")

        self._title_label = ctk.CTkLabel(
            self.content, text=title,
            font=ctk.CTkFont(size=13), anchor="w"
        )
        self._title_label.pack(fill="x")

        self._value_label = ctk.CTkLabel(
            self.content, text=value,
            font=ctk.CTkFont(size=28, weight="bold"), anchor="w"
        )
        self._value_label.pack(fill="x", pady=(4, 0))

        if subtitle:
            self._subtitle_label = ctk.CTkLabel(
                self.content, text=subtitle,
                font=ctk.CTkFont(size=11), text_color="gray", anchor="w"
            )
            self._subtitle_label.pack(fill="x", pady=(2, 0))

    def update_value(self, value: str) -> None:
        self._value_label.configure(text=value)


class TableView(ctk.CTkFrame):
    """Wraps a ttk.Treeview in a CTk frame with scrollbars."""

    def __init__(
        self, master, columns: List[str], column_widths: Optional[List[int]] = None,
        height: int = 400, **kwargs
    ):
        super().__init__(master, **kwargs)
        self._columns = columns
        self._data: List[Tuple[Any, ...]] = []

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            rowheight=32,
            fieldbackground="#2b2b2b",
            borderwidth=0,
            font=("Segoe UI", 11),
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#1f538d")])

        self._tree = ttk.Treeview(
            self, columns=columns, show="headings", height=height // 32,
            selectmode="browse",
        )

        for i, col in enumerate(columns):
            width = column_widths[i] if column_widths and i < len(column_widths) else 120
            self._tree.heading(col, text=col, anchor="w")
            self._tree.column(col, width=width, minwidth=80, anchor="w")

        v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        self._tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._tree.bind("<ButtonRelease-1>", self._on_select)

        self._on_select_callback: Optional[Callable] = None

    @property
    def tree(self) -> ttk.Treeview:
        return self._tree

    def set_data(self, rows: List[List[Any]]) -> None:
        self._data = rows
        self._tree.delete(*self._tree.get_children())
        for row in rows:
            self._tree.insert("", "end", values=tuple(row))

    def get_selected_row(self) -> Optional[Tuple[int, List[Any]]]:
        selection = self._tree.selection()
        if not selection:
            return None
        item = selection[0]
        values = self._tree.item(item, "values")
        idx = self._tree.index(item)
        return idx, list(values)

    def clear_selection(self) -> None:
        self._tree.selection_remove(self._tree.selection())

    def on_select(self, callback: Callable) -> None:
        self._on_select_callback = callback

    def _on_select(self, event) -> None:
        if self._on_select_callback:
            self._on_select_callback(self.get_selected_row())


class DialogBase(ctk.CTkToplevel):
    """Base class for dialog windows."""

    def __init__(self, master, title: str, width: int = 500, height: int = 400):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._result: Any = None

        self._center_on_parent(master)

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

    def get_result(self) -> Any:
        return self._result


class InfoDialog(DialogBase):
    """Simple information or error dialog."""

    def __init__(self, master, title: str, message: str,
                 dialog_type: str = "info", width: int = 400, height: int = 200):
        super().__init__(master, title, width, height)
        colors = {"info": "#1f538d", "success": "#2d8a4e", "error": "#a83232", "warning": "#b8860b"}
        color = colors.get(dialog_type, "#1f538d")

        icon_texts = {"info": "\u2139\ufe0f", "success": "\u2714\ufe0f",
                      "error": "\u2716\ufe0f", "warning": "\u26a0\ufe0f"}
        icon_text = icon_texts.get(dialog_type, "\u2139\ufe0f")

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(pady=(16, 8))
        ctk.CTkLabel(top, text=icon_text, font=ctk.CTkFont(size=36),
                     text_color=color).pack()

        use_textbox = height > 250 or len(message) > 200
        if use_textbox:
            self._msg_text = ctk.CTkTextbox(
                self, font=ctk.CTkFont(size=13), wrap="word",
                fg_color=("white", "#2b2b2b"), border_width=0,
            )
            self._msg_text.pack(padx=20, fill="both", expand=True)
            self._msg_text.insert("0.0", message)
            self._msg_text.configure(state="disabled")
        else:
            ctk.CTkLabel(
                self, text=message, font=ctk.CTkFont(size=14),
                wraplength=350, justify="center",
            ).pack(pady=(10, 20), padx=20, fill="both", expand=True)

        self._ok_button = ctk.CTkButton(
            self, text="OK", command=self.destroy, width=100,
            fg_color=color, hover_color=color
        )
        self._ok_button.pack(pady=(0, 20))


class ConfirmDialog(DialogBase):
    """Confirmation dialog with Yes/No buttons."""

    def __init__(self, master, title: str, message: str, width: int = 400, height: int = 180):
        super().__init__(master, title, width, height)

        self._message_label = ctk.CTkLabel(
            self, text=message, font=ctk.CTkFont(size=14),
            wraplength=350, justify="center"
        )
        self._message_label.pack(pady=(30, 20), padx=20, fill="both", expand=True)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))

        self._yes_button = ctk.CTkButton(
            btn_frame, text="Yes", width=100, command=self._on_yes,
            fg_color="#2d8a4e", hover_color="#236b3d"
        )
        self._yes_button.pack(side="left", padx=(0, 10))

        self._no_button = ctk.CTkButton(
            btn_frame, text="No", width=100, command=self._on_no,
            fg_color="#a83232", hover_color="#8a2828"
        )
        self._no_button.pack(side="left")

    def _on_yes(self) -> None:
        self._result = True
        self.destroy()

    def _on_no(self) -> None:
        self._result = False
        self.destroy()


class Tooltip:
    """A simple tooltip widget."""

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text = text
        self._tooltip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None) -> None:
        if self._tooltip_window:
            return
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + 20
        self._tooltip_window = ctk.CTkToplevel(self._widget)
        self._tooltip_window.wm_overrideredirect(True)
        self._tooltip_window.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(
            self._tooltip_window, text=self._text,
            font=ctk.CTkFont(size=11),
            fg_color="#353535", text_color="white",
            corner_radius=6, padx=10, pady=5,
        )
        label.pack()

    def _hide(self, event=None) -> None:
        if self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None


class SectionHeader(ctk.CTkFrame):
    """A styled section header with title and optional subtitle."""

    def __init__(self, master, title: str, subtitle: str = "", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._title_label = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        self._title_label.pack(fill="x")

        if subtitle:
            self._subtitle_label = ctk.CTkLabel(
                self, text=subtitle,
                font=ctk.CTkFont(size=12), text_color="gray", anchor="w"
            )
            self._subtitle_label.pack(fill="x", pady=(2, 0))


class ComplexityCard(ctk.CTkFrame):
    """Displays algorithm complexity information in a compact card."""

    def __init__(self, master, complexities: List[Dict[str, str]], **kwargs):
        super().__init__(master, fg_color=("#e8e8e8", "#2b2b2b"),
                         corner_radius=8, **kwargs)
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(
            inner, text="Algorithm Complexity",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        ).pack(fill="x")

        for item in complexities:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=(2, 0))
            ctk.CTkLabel(
                row, text=item.get("name", ""),
                font=ctk.CTkFont(size=11), anchor="w", width=130,
            ).pack(side="left")
            time = item.get("time", "")
            space = item.get("space", "")
            colors = {"O(1)": "#2d8a4e", "O(log n)": "#1f538d",
                      "O(n)": "#b8860b", "O(n log n)": "#6a1f8d",
                      "O(n^2)": "#a83232"}
            tc = colors.get(time.split(",")[0].strip(), "#888888")
            sc = colors.get(space.split(",")[0].strip(), "#888888")
            ctk.CTkLabel(
                row, text=f"Time: {time}", font=ctk.CTkFont(size=11),
                text_color=tc, anchor="w", width=120,
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=f"Space: {space}", font=ctk.CTkFont(size=11),
                text_color=sc, anchor="w",
            ).pack(side="left")


class ProgressOverlay(ctk.CTkFrame):
    """An overlay with a progress bar and status message."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=("#f0f0f0", "#1e1e2e"),
                         corner_radius=8, **kwargs)
        self._progress = ctk.CTkProgressBar(self, mode="indeterminate", height=6)
        self._progress.pack(fill="x", padx=20, pady=(16, 8))
        self._progress.start()
        self._label = ctk.CTkLabel(
            self, text="Processing...", font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
        )
        self._label.pack(pady=(0, 12))

    def set_text(self, text: str) -> None:
        self._label.configure(text=text)

    def stop(self) -> None:
        self._progress.stop()
        self._progress.pack_forget()
