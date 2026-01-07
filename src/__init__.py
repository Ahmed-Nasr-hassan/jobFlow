"""JobFlow - Production-grade Python script execution library.

A Clean Architecture library for executing Python scripts in different
environments with streaming log support.
"""

from .application import RunScriptUseCase
from .domain import (
    ScriptExecutor,
    LogSink,
    LogLevel,
    ExecutionResult,
    ExecutionStatus,
    ScriptConfig,
    DomainException,
    ScriptExecutionException,
    InvalidScriptException,
)
from .infrastructure import (
    LocalSubprocessExecutor,
    LambdaExecutor,
    WorkerExecutor,
    StdoutLogSink,
    SSELogSink,
    CompositeLogSink,
)

__version__ = "0.1.0"

__all__ = [
    # Application
    "RunScriptUseCase",
    # Domain
    "ScriptExecutor",
    "LogSink",
    "LogLevel",
    "ExecutionResult",
    "ExecutionStatus",
    "ScriptConfig",
    "DomainException",
    "ScriptExecutionException",
    "InvalidScriptException",
    # Infrastructure - Executors
    "LocalSubprocessExecutor",
    "LambdaExecutor",
    "WorkerExecutor",
    # Infrastructure - Log Sinks
    "StdoutLogSink",
    "SSELogSink",
    "CompositeLogSink",
]

