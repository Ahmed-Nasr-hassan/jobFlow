"""Lambda-style in-process executor implementation."""

import importlib.util
import sys
import time
from io import StringIO
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


class LambdaExecutor(ScriptExecutor):
    """Executes Python scripts in-process (Lambda-style).

    This executor runs scripts in the same process, capturing
    stdout/stderr and handling exceptions.
    """

    def __init__(
        self, file_provider: FileProvider | None = None, temp_directory: str = "/tmp"
    ) -> None:
        """Initialize the executor.

        Args:
            file_provider: Optional file provider for staging required files
            temp_directory: Directory for staging files (default: /tmp for Lambda)
        """
        self._file_provider = file_provider
        self._temp_directory = temp_directory

    def execute(
        self,
        config: ScriptConfig,
        log_sink: LogSink | None = None,
    ) -> ExecutionResult:
        """Execute a Python script synchronously in-process.

        Args:
            config: Script execution configuration
            log_sink: Optional log sink for streaming logs

        Returns:
            ExecutionResult containing execution outcome

        Raises:
            ScriptExecutionException: If execution fails
        """
        start_time = time.time()
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        staged_files: list[Path] = []

        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            # Stage required files if file provider is available
            if self._file_provider and config.file_requirements:
                staged_files = self._stage_files(config, log_sink)
            
            # Redirect stdout/stderr
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Set environment variables
            if config.environment_variables:
                import os

                for key, value in config.environment_variables.items():
                    os.environ[key] = value

            # Change working directory if specified
            if config.working_directory:
                import os

                original_cwd = os.getcwd()
                os.chdir(config.working_directory)
            else:
                original_cwd = None

            try:
                # Load and execute the script
                spec = importlib.util.spec_from_file_location("script", config.script_path)
                if spec is None or spec.loader is None:
                    raise ScriptExecutionException(f"Could not load script: {config.script_path}")

                module = importlib.util.module_from_spec(spec)
                sys.modules["script"] = module

                # Execute the script
                spec.loader.exec_module(module)

                exit_code = 0
                status = ExecutionStatus.SUCCESS

            except SystemExit as e:
                exit_code = e.code if isinstance(e.code, int) else 0
                status = ExecutionStatus.SUCCESS if exit_code == 0 else ExecutionStatus.FAILED
            except Exception as e:
                # Capture exception in stderr
                import traceback

                traceback.print_exc()
                exit_code = 1
                status = ExecutionStatus.FAILED

            finally:
                # Restore working directory
                if original_cwd:
                    import os

                    os.chdir(original_cwd)

                # Restore stdout/stderr
                sys.stdout = original_stdout
                sys.stderr = original_stderr

            # Get captured output
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()

            # Stream to log sink if available
            if log_sink:
                for line in stdout_content.splitlines():
                    log_sink.emit(LogLevel.INFO, line)
                for line in stderr_content.splitlines():
                    log_sink.emit(LogLevel.ERROR, line)

            duration = time.time() - start_time

            result = ExecutionResult(
                status=status,
                exit_code=exit_code,
                stdout=stdout_content,
                stderr=stderr_content,
                duration_seconds=duration,
                metadata=config.metadata,
            )

            # Upload output files if file provider is available
            if self._file_provider and config.file_outputs:
                self._upload_output_files(config, log_sink)

            return result

        except Exception as e:
            duration = time.time() - start_time
            # Restore stdout/stderr in case of error
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            raise ScriptExecutionException(f"In-process execution failed: {str(e)}") from e
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
        """Execute a Python script asynchronously in-process.

        Note: In-process execution is inherently synchronous, but we
        yield logs as they're captured to maintain async interface.

        Args:
            config: Script execution configuration
            log_sink: Optional log sink for streaming logs

        Yields:
            Either log messages (str) or the final ExecutionResult

        Raises:
            ScriptExecutionException: If execution fails
        """
        # For in-process execution, we run synchronously but yield results
        result = self.execute(config, log_sink)

        # Yield stdout lines
        for line in result.stdout.splitlines():
            yield line

        # Yield stderr lines
        for line in result.stderr.splitlines():
            yield line

        # Yield final result
        yield result

    def _stage_files(self, config: ScriptConfig, log_sink: LogSink | None = None) -> list[Path]:
        """Stage required files before execution in Lambda context.

        Files are staged to /tmp (or configured temp_directory) which is
        the writable space in Lambda environment.

        Args:
            config: Script configuration
            log_sink: Optional log sink for logging file staging

        Returns:
            List of staged file paths for cleanup

        Raises:
            ScriptExecutionException: If file staging fails
        """
        staged_files: list[Path] = []
        # Use temp_directory (default /tmp) for Lambda, or working_directory if specified
        working_dir = (
            Path(config.working_directory)
            if config.working_directory
            else Path(self._temp_directory)
        )

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

    def _upload_output_files(self, config: ScriptConfig, log_sink: LogSink | None = None) -> None:
        """Upload output files after execution in Lambda context.

        Args:
            config: Script configuration
            log_sink: Optional log sink for logging file uploads

        Raises:
            ScriptExecutionException: If required output file upload fails
        """
        # Use temp_directory (default /tmp) for Lambda, or working_directory if specified
        working_dir = (
            Path(config.working_directory)
            if config.working_directory
            else Path(self._temp_directory)
        )

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

