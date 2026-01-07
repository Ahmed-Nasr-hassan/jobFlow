"""Domain layer - Pure business rules and interfaces.

This layer contains no dependencies on infrastructure, frameworks, or external libraries.
"""

from .executor import ScriptExecutor
from .file_provider import FileProvider
from .logging import LogSink, LogLevel
from .models import ExecutionResult, ExecutionStatus, FileRequirement, FileOutput, ScriptConfig
from .exceptions import (
    DomainException,
    ScriptExecutionException,
    InvalidScriptException,
)

__all__ = [
    "ScriptExecutor",
    "FileProvider",
    "LogSink",
    "LogLevel",
    "ExecutionResult",
    "ExecutionStatus",
    "FileRequirement",
    "FileOutput",
    "ScriptConfig",
    "DomainException",
    "ScriptExecutionException",
    "InvalidScriptException",
]

