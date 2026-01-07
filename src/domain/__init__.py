"""Domain layer - Pure business rules and interfaces.

This layer contains no dependencies on infrastructure, frameworks, or external libraries.
"""

from .executor import ScriptExecutor
from .logging import LogSink, LogLevel
from .models import ExecutionResult, ScriptConfig
from .exceptions import (
    DomainException,
    ScriptExecutionException,
    InvalidScriptException,
)

__all__ = [
    "ScriptExecutor",
    "LogSink",
    "LogLevel",
    "ExecutionResult",
    "ScriptConfig",
    "DomainException",
    "ScriptExecutionException",
    "InvalidScriptException",
]

