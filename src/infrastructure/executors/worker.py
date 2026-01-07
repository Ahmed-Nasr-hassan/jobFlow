"""Remote worker executor implementation (stub/interface)."""

import time
from typing import AsyncIterator

from ...domain import (
    ScriptExecutor,
    ScriptConfig,
    ExecutionResult,
    ExecutionStatus,
    LogSink,
    ScriptExecutionException,
)


class WorkerExecutor(ScriptExecutor):
    """Executes Python scripts via remote worker (stub implementation).

    This is a placeholder implementation that demonstrates the interface.
    In production, this would communicate with a remote worker service
    (e.g., via HTTP, message queue, gRPC, etc.).
    """

    def __init__(self, worker_endpoint: str | None = None) -> None:
        """Initialize the executor.

        Args:
            worker_endpoint: Optional endpoint URL for worker service
        """
        self._worker_endpoint = worker_endpoint or "http://localhost:8000/worker"

    def execute(
        self,
        config: ScriptConfig,
        log_sink: LogSink | None = None,
    ) -> ExecutionResult:
        """Execute a Python script via remote worker.

        Args:
            config: Script execution configuration
            log_sink: Optional log sink for streaming logs

        Returns:
            ExecutionResult containing execution outcome

        Raises:
            ScriptExecutionException: If execution fails

        Note:
            This is a stub implementation. In production, this would:
            1. Serialize the script config
            2. Send request to worker endpoint
            3. Poll for results or use webhooks
            4. Stream logs back via log sink
        """
        # Stub implementation - raise exception to indicate not implemented
        raise ScriptExecutionException(
            "WorkerExecutor is a stub. Implement remote worker communication "
            "by extending this class or providing a concrete implementation."
        )

    async def execute_async(
        self,
        config: ScriptConfig,
        log_sink: LogSink | None = None,
    ) -> AsyncIterator[ExecutionResult | str]:
        """Execute a Python script asynchronously via remote worker.

        Args:
            config: Script execution configuration
            log_sink: Optional log sink for streaming logs

        Yields:
            Either log messages (str) or the final ExecutionResult

        Raises:
            ScriptExecutionException: If execution fails

        Note:
            This is a stub implementation. In production, this would:
            1. Establish connection to worker (WebSocket, SSE, etc.)
            2. Stream logs as they arrive
            3. Yield final result when complete
        """
        # Stub implementation
        raise ScriptExecutionException(
            "WorkerExecutor is a stub. Implement remote worker communication "
            "by extending this class or providing a concrete implementation."
        )

