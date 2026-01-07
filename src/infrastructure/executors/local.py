"""Local subprocess executor implementation."""

import asyncio
import subprocess
import time
from typing import AsyncIterator

from pathlib import Path

from ...domain import (
    ScriptExecutor,
    ScriptConfig,
    ExecutionResult,
    ExecutionStatus,
    LogSink,
    LogLevel,
    ScriptExecutionException,
    FileProvider,
)


class LocalSubprocessExecutor(ScriptExecutor):
    """Executes Python scripts as local subprocesses."""

    def __init__(
        self, python_executable: str = "python3", file_provider: FileProvider | None = None
    ) -> None:
        """Initialize the executor.

        Args:
            python_executable: Path to Python executable (default: python3)
            file_provider: Optional file provider for staging required files
        """
        self._python_executable = python_executable
        self._file_provider = file_provider

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

            result = ExecutionResult(
                status=status,
                exit_code=exit_code,
                stdout="\n".join(stdout_lines),
                stderr="\n".join(stderr_lines),
                duration_seconds=duration,
                metadata=config.metadata,
            )

            # Upload output files if file provider is available
            if self._file_provider and config.file_outputs:
                self._upload_output_files(config, log_sink)

            return result

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
        finally:
            # Cleanup staged files
            if self._file_provider:
                for staged_file in staged_files:
                    self._file_provider.cleanup(staged_file)

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
        staged_files: list[Path] = []

        try:
            # Stage required files if file provider is available
            if self._file_provider and config.file_requirements:
                staged_files = await self._stage_files_async(config)

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

            # Upload output files if file provider is available
            if self._file_provider and config.file_outputs:
                await self._upload_output_files_async(config)

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
        finally:
            # Cleanup staged files
            if self._file_provider:
                for staged_file in staged_files:
                    self._file_provider.cleanup(staged_file)

    def _stage_files(self, config: ScriptConfig, log_sink: LogSink | None = None) -> list[Path]:
        """Stage required files before execution.

        Args:
            config: Script configuration
            log_sink: Optional log sink for logging file staging

        Returns:
            List of staged file paths for cleanup

        Raises:
            ScriptExecutionException: If file staging fails
        """
        staged_files: list[Path] = []
        working_dir = Path(config.working_directory) if config.working_directory else Path.cwd()

        if not config.file_requirements:
            return staged_files

        for file_req in config.file_requirements:
            try:
                destination = working_dir / file_req.destination
                staged_path = self._file_provider.get_file(file_req.source, str(destination))
                staged_files.append(staged_path)

                if log_sink:
                    log_sink.emit(
                        LogLevel.INFO, f"Staged file: {file_req.source} -> {destination}"
                    )
            except FileNotFoundError as e:
                if file_req.required:
                    raise ScriptExecutionException(f"Required file not found: {file_req.source}") from e
                # Non-required files are skipped
                if log_sink:
                    log_sink.emit(
                        LogLevel.WARNING, f"Optional file not found (skipping): {file_req.source}"
                    )
            except Exception as e:
                if file_req.required:
                    raise ScriptExecutionException(
                        f"Failed to stage required file {file_req.source}: {str(e)}"
                    ) from e

        return staged_files

    async def _stage_files_async(self, config: ScriptConfig) -> list[Path]:
        """Stage required files asynchronously before execution.

        Args:
            config: Script configuration

        Returns:
            List of staged file paths for cleanup

        Raises:
            ScriptExecutionException: If file staging fails
        """
        staged_files: list[Path] = []
        working_dir = Path(config.working_directory) if config.working_directory else Path.cwd()

        if not config.file_requirements:
            return staged_files

        for file_req in config.file_requirements:
            try:
                destination = working_dir / file_req.destination
                staged_path = await self._file_provider.get_file_async(
                    file_req.source, str(destination)
                )
                staged_files.append(staged_path)
            except FileNotFoundError as e:
                if file_req.required:
                    raise ScriptExecutionException(f"Required file not found: {file_req.source}") from e
            except Exception as e:
                if file_req.required:
                    raise ScriptExecutionException(
                        f"Failed to stage required file {file_req.source}: {str(e)}"
                    ) from e

        return staged_files

    def _upload_output_files(self, config: ScriptConfig, log_sink: LogSink | None = None) -> None:
        """Upload output files after execution.

        Args:
            config: Script configuration
            log_sink: Optional log sink for logging file uploads

        Raises:
            ScriptExecutionException: If required output file upload fails
        """
        working_dir = Path(config.working_directory) if config.working_directory else Path.cwd()

        if not config.file_outputs:
            return

        for file_output in config.file_outputs:
            try:
                source_path = working_dir / file_output.source

                if not source_path.exists():
                    if file_output.required:
                        raise ScriptExecutionException(
                            f"Required output file not found: {file_output.source}"
                        )
                    # Non-required outputs are skipped
                    if log_sink:
                        log_sink.emit(
                            LogLevel.WARNING,
                            f"Optional output file not found (skipping): {file_output.source}",
                        )
                    continue

                # Upload file to destination
                uploaded_path = self._file_provider.put_file(source_path, file_output.destination)

                if log_sink:
                    log_sink.emit(
                        LogLevel.INFO,
                        f"Uploaded output file: {file_output.source} -> {uploaded_path}",
                    )
            except Exception as e:
                if file_output.required:
                    raise ScriptExecutionException(
                        f"Failed to upload required output file {file_output.source}: {str(e)}"
                    ) from e
                # Non-required outputs log warning but don't fail
                if log_sink:
                    log_sink.emit(
                        LogLevel.WARNING,
                        f"Failed to upload optional output file {file_output.source}: {str(e)}",
                    )

    async def _upload_output_files_async(self, config: ScriptConfig) -> None:
        """Upload output files asynchronously after execution.

        Args:
            config: Script configuration

        Raises:
            ScriptExecutionException: If required output file upload fails
        """
        working_dir = Path(config.working_directory) if config.working_directory else Path.cwd()

        if not config.file_outputs:
            return

        for file_output in config.file_outputs:
            try:
                source_path = working_dir / file_output.source

                if not source_path.exists():
                    if file_output.required:
                        raise ScriptExecutionException(
                            f"Required output file not found: {file_output.source}"
                        )
                    continue

                # Upload file to destination asynchronously
                await self._file_provider.put_file_async(source_path, file_output.destination)
            except Exception as e:
                if file_output.required:
                    raise ScriptExecutionException(
                        f"Failed to upload required output file {file_output.source}: {str(e)}"
                    ) from e

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

