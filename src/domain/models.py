"""Domain models - Value objects and entities."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ExecutionStatus(str, Enum):
    """Status of script execution."""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ScriptConfig:
    """Configuration for script execution."""

    script_path: str
    working_directory: str | None = None
    environment_variables: dict[str, str] | None = None
    timeout_seconds: int | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.script_path:
            raise ValueError("script_path cannot be empty")


@dataclass(frozen=True)
class ExecutionResult:
    """Result of script execution."""

    status: ExecutionStatus
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    metadata: dict[str, Any] | None = None

    @property
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS

