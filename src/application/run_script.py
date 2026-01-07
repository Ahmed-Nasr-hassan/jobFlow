"""Run script use case - Orchestrates script execution."""

import time
from typing import AsyncIterator

from ..domain import (
    ScriptExecutor,
    LogSink,
    ScriptConfig,
    ExecutionResult,
    ExecutionStatus,
    ScriptExecutionException,
)


class RunScriptUseCase:
    """Use case for executing Python scripts.

    Orchestrates script execution, handles lifecycle events,
    and manages log streaming.
    """

    def __init__(self, executor: ScriptExecutor, log_sink: LogSink | None = None) -> None:
        """Initialize the use case.

        Args:
            executor: Script executor implementation
            log_sink: Optional log sink for streaming logs
        """
        self._executor = executor
        self._log_sink = log_sink

    def execute(self, config: ScriptConfig) -> ExecutionResult:
        """Execute a script synchronously.

        Args:
            config: Script execution configuration

        Returns:
            ExecutionResult containing execution outcome

        Raises:
            ScriptExecutionException: If execution fails
        """
        self._emit_log("INFO", f"Starting script execution: {config.script_path}")

        try:
            start_time = time.time()
            result = self._executor.execute(config, self._log_sink)
            duration = time.time() - start_time

            # Create result with actual duration if not set
            if result.duration_seconds == 0.0:
                result = ExecutionResult(
                    status=result.status,
                    exit_code=result.exit_code,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    duration_seconds=duration,
                    metadata=result.metadata,
                )

            self._emit_log(
                "INFO",
                f"Script execution completed: {result.status.value} (exit_code={result.exit_code})",
            )

            return result

        except ScriptExecutionException as e:
            self._emit_log("ERROR", f"Script execution failed: {str(e)}")
            raise
        except Exception as e:
            self._emit_log("ERROR", f"Unexpected error during execution: {str(e)}")
            raise ScriptExecutionException(f"Unexpected error: {str(e)}") from e

    async def execute_async(self, config: ScriptConfig) -> AsyncIterator[ExecutionResult | str]:
        """Execute a script asynchronously, yielding logs and final result.

        Args:
            config: Script execution configuration

        Yields:
            Either log messages (str) or the final ExecutionResult

        Raises:
            ScriptExecutionException: If execution fails
        """
        self._emit_log("INFO", f"Starting async script execution: {config.script_path}")

        try:
            async for item in self._executor.execute_async(config, self._log_sink):
                if isinstance(item, str):
                    # Forward log messages
                    yield item
                elif isinstance(item, ExecutionResult):
                    # Final result
                    self._emit_log(
                        "INFO",
                        f"Script execution completed: {item.status.value} (exit_code={item.exit_code})",
                    )
                    yield item

        except ScriptExecutionException as e:
            self._emit_log("ERROR", f"Script execution failed: {str(e)}")
            raise
        except Exception as e:
            self._emit_log("ERROR", f"Unexpected error during execution: {str(e)}")
            raise ScriptExecutionException(f"Unexpected error: {str(e)}") from e

    def _emit_log(self, level: str, message: str) -> None:
        """Emit a log message through the log sink if available.

        Args:
            level: Log level (INFO, ERROR, etc.)
            message: Log message
        """
        if self._log_sink:
            from ..domain import LogLevel

            try:
                log_level = LogLevel(level.upper())
                self._log_sink.emit(log_level, message)
            except (ValueError, AttributeError):
                # Fallback if log level is invalid
                self._log_sink.emit(LogLevel.INFO, message)

