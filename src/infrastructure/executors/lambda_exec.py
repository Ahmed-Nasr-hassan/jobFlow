"""Lambda-style in-process executor implementation."""

import importlib.util
import sys
import time
from io import StringIO
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


class LambdaExecutor(ScriptExecutor):
    """Executes Python scripts in-process (Lambda-style).

    This executor runs scripts in the same process, capturing
    stdout/stderr and handling exceptions.
    """

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

        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
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

            return ExecutionResult(
                status=status,
                exit_code=exit_code,
                stdout=stdout_content,
                stderr=stderr_content,
                duration_seconds=duration,
                metadata=config.metadata,
            )

        except Exception as e:
            duration = time.time() - start_time
            # Restore stdout/stderr in case of error
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            raise ScriptExecutionException(f"In-process execution failed: {str(e)}") from e

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

