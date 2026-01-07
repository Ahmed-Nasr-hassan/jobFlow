"""Server-Sent Events (SSE) log sink implementation."""

import json
from typing import Any, Callable

from ...domain import LogSink, LogLevel


class SSELogSink(LogSink):
    """Log sink that emits logs via Server-Sent Events.

    This sink uses a callback function to send SSE-formatted messages.
    The callback should accept a string (the SSE-formatted message).
    """

    def __init__(self, send_callback: Callable[[str], None]) -> None:
        """Initialize the SSE log sink.

        Args:
            send_callback: Function that sends SSE-formatted messages.
                          Should accept a single string argument (the SSE data).
        """
        self._send_callback = send_callback
        self._closed = False

    def emit(self, level: LogLevel, message: str, metadata: dict[str, str] | None = None) -> None:
        """Emit a log message as SSE.

        Args:
            level: Log severity level
            message: Log message content
            metadata: Optional metadata dictionary
        """
        if self._closed:
            return

        # Format as SSE event
        event_data = {
            "level": level.value,
            "message": message,
        }

        if metadata:
            event_data["metadata"] = metadata

        # SSE format: data: <json>\n\n
        sse_message = f"data: {json.dumps(event_data)}\n\n"

        try:
            self._send_callback(sse_message)
        except Exception:
            # Silently fail if callback raises (e.g., connection closed)
            pass

    def close(self) -> None:
        """Close the log sink."""
        self._closed = True

