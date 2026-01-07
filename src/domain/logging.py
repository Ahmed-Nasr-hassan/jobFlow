"""Domain logging interfaces."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class LogLevel(str, Enum):
    """Log severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogSink(ABC):
    """Abstract interface for log sinks.

    Implementations handle the actual delivery of log messages
    to various destinations (SSE, stdout, files, etc.).
    """

    @abstractmethod
    def emit(self, level: LogLevel, message: str, metadata: dict[str, str] | None = None) -> None:
        """Emit a log message.

        Args:
            level: Log severity level
            message: Log message content
            metadata: Optional metadata dictionary
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the log sink and release resources."""
        pass

    def __enter__(self) -> "LogSink":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

