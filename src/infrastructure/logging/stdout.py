"""Stdout log sink implementation."""

import sys
from typing import Any

from ...domain import LogSink, LogLevel


class StdoutLogSink(LogSink):
    """Log sink that writes to stdout/stderr."""

    def __init__(self, use_stderr_for_errors: bool = True) -> None:
        """Initialize the stdout log sink.

        Args:
            use_stderr_for_errors: If True, write ERROR/CRITICAL to stderr, else stdout
        """
        self._use_stderr_for_errors = use_stderr_for_errors

    def emit(self, level: LogLevel, message: str, metadata: dict[str, str] | None = None) -> None:
        """Emit a log message to stdout/stderr.

        Args:
            level: Log severity level
            message: Log message content
            metadata: Optional metadata dictionary (not printed, but available for extension)
        """
        formatted_message = self._format_message(level, message, metadata)

        if self._use_stderr_for_errors and level in (LogLevel.ERROR, LogLevel.CRITICAL):
            print(formatted_message, file=sys.stderr)
        else:
            print(formatted_message, file=sys.stdout)

    def close(self) -> None:
        """Close the log sink (no-op for stdout)."""
        pass

    def _format_message(self, level: LogLevel, message: str, metadata: dict[str, str] | None) -> str:
        """Format log message.

        Args:
            level: Log level
            message: Message content
            metadata: Optional metadata

        Returns:
            Formatted log message
        """
        return f"[{level.value}] {message}"

