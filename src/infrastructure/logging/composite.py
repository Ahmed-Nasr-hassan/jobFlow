"""Composite log sink implementation (fan-out pattern)."""

from typing import Any

from ...domain import LogSink, LogLevel


class CompositeLogSink(LogSink):
    """Composite log sink that forwards logs to multiple sinks (fan-out pattern).

    This allows logging to multiple destinations simultaneously
    (e.g., both SSE and stdout, or file and Kafka).
    """

    def __init__(self, *sinks: LogSink) -> None:
        """Initialize the composite log sink.

        Args:
            *sinks: Variable number of log sinks to forward messages to
        """
        self._sinks = list(sinks)
        self._closed = False

    def emit(self, level: LogLevel, message: str, metadata: dict[str, str] | None = None) -> None:
        """Emit a log message to all sinks.

        Args:
            level: Log severity level
            message: Log message content
            metadata: Optional metadata dictionary
        """
        if self._closed:
            return

        # Forward to all sinks, ignoring individual failures
        for sink in self._sinks:
            try:
                sink.emit(level, message, metadata)
            except Exception:
                # Continue to other sinks even if one fails
                pass

    def close(self) -> None:
        """Close all underlying log sinks."""
        if self._closed:
            return

        self._closed = True
        for sink in self._sinks:
            try:
                sink.close()
            except Exception:
                # Continue closing other sinks even if one fails
                pass

    def add_sink(self, sink: LogSink) -> None:
        """Add a new log sink to the composite.

        Args:
            sink: Log sink to add
        """
        if not self._closed:
            self._sinks.append(sink)

    def remove_sink(self, sink: LogSink) -> None:
        """Remove a log sink from the composite.

        Args:
            sink: Log sink to remove
        """
        if sink in self._sinks:
            self._sinks.remove(sink)

