"""Infrastructure layer - Adapters and implementations."""

from .executors.local import LocalSubprocessExecutor
from .executors.lambda_exec import LambdaExecutor
from .executors.worker import WorkerExecutor

from .file_providers.local import LocalFileProvider
from .file_providers.s3 import S3FileProvider
from .file_providers.http import HTTPFileProvider
from .file_providers.composite import CompositeFileProvider

from .logging.stdout import StdoutLogSink
from .logging.sse import SSELogSink
from .logging.composite import CompositeLogSink

__all__ = [
    # Executors
    "LocalSubprocessExecutor",
    "LambdaExecutor",
    "WorkerExecutor",
    # File Providers
    "LocalFileProvider",
    "S3FileProvider",
    "HTTPFileProvider",
    "CompositeFileProvider",
    # Log Sinks
    "StdoutLogSink",
    "SSELogSink",
    "CompositeLogSink",
]

