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
class FileRequirement:
    """File requirement for script execution.

    Maps a source file location to a destination path where
    the script expects to find it.
    """

    source: str  # Source path (format depends on FileProvider: local path, s3://, http://, etc.)
    destination: str  # Relative path where script expects the file (relative to working_directory)
    required: bool = True  # If False, missing file won't cause failure

    def __post_init__(self) -> None:
        """Validate file requirement."""
        if not self.source:
            raise ValueError("source cannot be empty")
        if not self.destination:
            raise ValueError("destination cannot be empty")


@dataclass(frozen=True)
class FileOutput:
    """Output file to upload after script execution.

    Maps a local file created by the script to a destination
    where it should be uploaded (S3, local, HTTP endpoint, etc.).
    """

    source: str  # Relative path where script creates the file (relative to working_directory)
    destination: str  # Destination path (format depends on FileProvider: local path, s3://, http://, etc.)
    required: bool = False  # If False, missing output file won't cause failure

    def __post_init__(self) -> None:
        """Validate file output."""
        if not self.source:
            raise ValueError("source cannot be empty")
        if not self.destination:
            raise ValueError("destination cannot be empty")


@dataclass(frozen=True)
class ScriptConfig:
    """Configuration for script execution."""

    script_path: str
    working_directory: str | None = None
    environment_variables: dict[str, str] | None = None
    timeout_seconds: int | None = None
    file_requirements: list[FileRequirement] | None = None
    file_outputs: list[FileOutput] | None = None
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

