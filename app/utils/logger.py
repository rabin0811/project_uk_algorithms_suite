import logging
import os
from datetime import datetime
from typing import Optional


class LoggerSetup:
    """Configures application-wide logging with file and console handlers."""

    _instance: Optional["LoggerSetup"] = None

    def __new__(cls, *args, **kwargs) -> "LoggerSetup":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self._ensure_log_directory()
        self._configure_root_logger()

    def _ensure_log_directory(self) -> None:
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def _configure_root_logger(self) -> None:
        log_file = os.path.join(
            self.log_dir,
            f'app_{datetime.now().strftime("%Y%m%d")}.log'
        )
        logging.basicConfig(
            level=self.log_level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Retrieve a logger instance for the given module name."""
        return logging.getLogger(name)
