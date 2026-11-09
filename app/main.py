"""
Algorithms & Data Structures Management Suite

A comprehensive desktop application demonstrating:
  - Linear Search, Binary Search
  - Merge Sort, Quick Sort
  - FCFS, SJF, Round Robin, Priority Scheduling
  - Interval Overlap Detection
  - Data Structures: Lists, Dictionaries, Queues, Heaps/Priority Queues

Modules:
  1. Inventory Management System
  2. Shared Resource Scheduling System
  3. Dynamic Resource Allocation System

Architecture: MVC (Model-View-Controller) with OOP principles.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import load_config
from utils.logger import LoggerSetup
from views.app import App


def main() -> None:
    """Application entry point. Loads config, initializes logger, launches UI."""
    config = load_config()
    LoggerSetup(
        log_dir=config.get("log_dir", "logs"),
        log_level=config.get("log_level", "INFO"),
    )
    app = App(config)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
