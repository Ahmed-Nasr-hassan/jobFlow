"""Domain executor interfaces."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from .logging import LogSink, LogLevel
from .models import ExecutionResult, ScriptConfig


class ScriptExecutor(ABC):
    """Abstract interface for script executors.

    Implementations handle the actual execution of Python scripts
    in various environments (local, Lambda, worker, etc.).
    """

    @abstractmethod
    def execute(
        self,
        config: ScriptConfig,
        log_sink: LogSink | None = None,
    ) -> ExecutionResult:
        """Execute a Python script synchronously.

        Args:
            config: Script execution configuration
            log_sink: Optional log sink for streaming logs

        Returns:
            ExecutionResult containing execution outcome

        Raises:
            ScriptExecutionException: If execution fails
        """
        pass

    @abstractmethod
    async def execute_async(
        self,
        config: ScriptConfig,
        log_sink: LogSink | None = None,
    ) -> AsyncIterator[ExecutionResult | str]:
        """Execute a Python script asynchronously, yielding logs and final result.

        Args:
            config: Script execution configuration
            log_sink: Optional log sink for streaming logs

        Yields:
            Either log messages (str) or the final ExecutionResult

        Raises:
            ScriptExecutionException: If execution fails
        """
        pass

