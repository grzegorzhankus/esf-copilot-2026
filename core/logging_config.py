"""Logging configuration for e-SF Copilot.

This module provides centralized logging configuration with:
- File rotation (size-based and time-based)
- JSON structured logging
- Console and file handlers
- Configurable log levels

Usage:
    from core.logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("Analysis started", extra={"filename": "test.xml"})
"""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

# Default configuration
DEFAULT_LOG_DIR = Path("logs")
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in [
                    "name", "msg", "args", "created", "filename",
                    "funcName", "levelname", "levelno", "lineno",
                    "module", "msecs", "pathname", "process",
                    "processName", "relativeCreated", "stack_info",
                    "exc_info", "exc_text", "thread", "threadName",
                    "message"
                ]:
                    try:
                        json.dumps(value)  # Check if serializable
                        log_data[key] = value
                    except (TypeError, ValueError):
                        log_data[key] = str(value)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Colored console formatter for readable output."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET

        # Format timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Basic format
        formatted = f"{timestamp} {color}{record.levelname:8}{reset} [{record.name}] {record.getMessage()}"

        # Add exception if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


class LoggingManager:
    """Centralized logging manager."""

    _instance: Optional["LoggingManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "LoggingManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._loggers: Dict[str, logging.Logger] = {}
            self._configured = False
            LoggingManager._initialized = True

    def configure(
        self,
        log_dir: Optional[Path] = None,
        log_level: Optional[int] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_json: bool = False,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT
    ) -> None:
        """Configure logging system.

        Args:
            log_dir: Directory for log files.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            enable_console: Enable console output.
            enable_file: Enable file output.
            enable_json: Use JSON format for file logs.
            max_bytes: Maximum size per log file.
            backup_count: Number of backup files to keep.
        """
        if self._configured:
            return

        # Get configuration from environment
        log_level = log_level or getattr(
            logging,
            os.getenv("LOG_LEVEL", "INFO").upper(),
            DEFAULT_LOG_LEVEL
        )
        log_dir = log_dir or Path(os.getenv("LOG_DIR", str(DEFAULT_LOG_DIR)))

        # Create log directory
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Remove existing handlers
        root_logger.handlers.clear()

        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(ConsoleFormatter())
            root_logger.addHandler(console_handler)

        # File handler
        if enable_file:
            log_file = log_dir / "esf_copilot.log"

            if enable_json:
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8"
                )
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8"
                )
                file_handler.setFormatter(logging.Formatter(
                    "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                ))

            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)

        # Error file handler (separate file for errors)
        error_file = log_dir / "esf_copilot_errors.log"
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(name)s] %(message)s\n%(exc_info)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        root_logger.addHandler(error_handler)

        self._configured = True

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger.

        Args:
            name: Logger name (usually __name__).

        Returns:
            Configured logger instance.
        """
        if not self._configured:
            self.configure()

        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)

        return self._loggers[name]


# Global logging manager instance
_manager = LoggingManager()


def configure_logging(**kwargs) -> None:
    """Configure the logging system.

    Args:
        **kwargs: Configuration options passed to LoggingManager.configure()
    """
    _manager.configure(**kwargs)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (usually __name__).

    Returns:
        Configured logger instance.

    Example:
        >>> from core.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started", extra={"file": "test.xml"})
    """
    return _manager.get_logger(name)


def log_analysis_event(
    event_type: str,
    file_name: str,
    **kwargs
) -> None:
    """Log an analysis-related event.

    Args:
        event_type: Type of event (e.g., "analysis_started", "analysis_completed").
        file_name: Name of the file being analyzed.
        **kwargs: Additional event data.
    """
    logger = get_logger("esf_copilot.analysis")
    logger.info(
        f"{event_type}: {file_name}",
        extra={"event_type": event_type, "file_name": file_name, **kwargs}
    )


def log_llm_event(
    event_type: str,
    model: str,
    **kwargs
) -> None:
    """Log an LLM-related event.

    Args:
        event_type: Type of event (e.g., "query_sent", "response_received").
        model: Model name.
        **kwargs: Additional event data.
    """
    logger = get_logger("esf_copilot.llm")
    logger.info(
        f"{event_type}: {model}",
        extra={"event_type": event_type, "model": model, **kwargs}
    )


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Log an error with context.

    Args:
        error: The exception that occurred.
        context: Additional context information.
    """
    logger = get_logger("esf_copilot.error")
    logger.error(
        str(error),
        exc_info=error,
        extra=context or {}
    )
