"""Local subprocess executor implementation."""

import asyncio
import subprocess
import time
from typing import AsyncIterator

from ...domain import (
    ScriptExecutor,
    ScriptConfig,
    ExecutionResult,
    ExecutionStatus,
    LogSink,
    LogLevel,
    ScriptExecutionException,
)


class LocalSubprocessExecutor(ScriptExecutor):
    """Executes Python scripts as local subprocesses."""

    def __init__(self, python_executable: str = "python3") -> None:
        """Initialize the executor.

        Args:
            python_executable: Path to Python executable (default: python3)
        """
        self._python_executable = python_executable

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
        start_time = time.time()

        try:
            # Build environment
            env = self._build_environment(config)

            # Build command
            cmd = [self._python_executable, config.script_path]

            # Execute subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=config.working_directory,
                env=env,
            )

            # Stream output if log sink is provided
            stdout_lines: list[str] = []
            stderr_lines: list[str] = []

            if log_sink:
                # Read output line by line using communicate with real-time streaming
                # For true streaming, we'd need threading, but for simplicity we'll
                # read after completion and stream to log sink
                stdout, stderr = process.communicate()
                exit_code = process.returncode

                # Stream to log sink
                if stdout:
                    for line in stdout.splitlines():
                        line = line.rstrip("\n\r")
                        stdout_lines.append(line)
                        log_sink.emit(LogLevel.INFO, line)
                if stderr:
                    for line in stderr.splitlines():
                        line = line.rstrip("\n\r")
                        stderr_lines.append(line)
                        log_sink.emit(LogLevel.ERROR, line)
            else:
                # Wait and capture all output
                stdout, stderr = process.communicate()
                exit_code = process.returncode
                stdout_lines = stdout.splitlines() if stdout else []
                stderr_lines = stderr.splitlines() if stderr else []

            duration = time.time() - start_time

            # Determine status
            if exit_code == 0:
                status = ExecutionStatus.SUCCESS
            else:
                status = ExecutionStatus.FAILED

            return ExecutionResult(
                status=status,
                exit_code=exit_code,
                stdout="\n".join(stdout_lines),
                stderr="\n".join(stderr_lines),
                duration_seconds=duration,
                metadata=config.metadata,
            )

        except FileNotFoundError:
            raise ScriptExecutionException(
                f"Python executable not found: {self._python_executable}"
            )
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            raise ScriptExecutionException(
                f"Script execution timed out after {config.timeout_seconds} seconds",
                exit_code=None,
            )
        except Exception as e:
            duration = time.time() - start_time
            raise ScriptExecutionException(f"Subprocess execution failed: {str(e)}") from e

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
        start_time = time.time()

        try:
            # Build environment
            env = self._build_environment(config)

            # Build command
            cmd = [self._python_executable, config.script_path]

            # Create async subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=config.working_directory,
                env=env,
            )

            stdout_lines: list[str] = []
            stderr_lines: list[str] = []

            # Stream stdout
            if process.stdout:
                async for line in process.stdout:
                    line_str = line.decode("utf-8").rstrip("\n\r")
                    stdout_lines.append(line_str)
                    if log_sink:
                        log_sink.emit(LogLevel.INFO, line_str)
                    yield line_str

            # Stream stderr
            if process.stderr:
                async for line in process.stderr:
                    line_str = line.decode("utf-8").rstrip("\n\r")
                    stderr_lines.append(line_str)
                    if log_sink:
                        log_sink.emit(LogLevel.ERROR, line_str)
                    yield line_str

            # Wait for completion
            exit_code = await process.wait()
            duration = time.time() - start_time

            # Determine status
            if exit_code == 0:
                status = ExecutionStatus.SUCCESS
            else:
                status = ExecutionStatus.FAILED

            result = ExecutionResult(
                status=status,
                exit_code=exit_code,
                stdout="\n".join(stdout_lines),
                stderr="\n".join(stderr_lines),
                duration_seconds=duration,
                metadata=config.metadata,
            )

            yield result

        except FileNotFoundError:
            raise ScriptExecutionException(
                f"Python executable not found: {self._python_executable}"
            )
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            raise ScriptExecutionException(
                f"Script execution timed out after {config.timeout_seconds} seconds",
                exit_code=None,
            )
        except Exception as e:
            duration = time.time() - start_time
            raise ScriptExecutionException(f"Async subprocess execution failed: {str(e)}") from e

    def _build_environment(self, config: ScriptConfig) -> dict[str, str] | None:
        """Build environment variables for subprocess.

        Args:
            config: Script configuration

        Returns:
            Environment dictionary or None to inherit from parent
        """
        if config.environment_variables:
            import os

            env = os.environ.copy()
            env.update(config.environment_variables)
            return env
        return None

