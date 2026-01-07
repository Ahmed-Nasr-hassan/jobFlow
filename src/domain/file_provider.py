"""Domain file provider interfaces."""

from abc import ABC, abstractmethod
from pathlib import Path


class FileProvider(ABC):
    """Abstract interface for file providers.

    Implementations handle file access from various sources
    (local filesystem, S3, HTTP, etc.) and make them available
    to scripts during execution.
    """

    @abstractmethod
    def get_file(self, source_path: str, destination_path: str) -> Path:
        """Retrieve a file from source and make it available at destination.

        Args:
            source_path: Path to the source file (format depends on provider)
            destination_path: Local path where the file should be available

        Returns:
            Path object pointing to the local file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If file access is denied
        """
        pass

    @abstractmethod
    def get_file_async(self, source_path: str, destination_path: str) -> Path:
        """Retrieve a file asynchronously from source and make it available at destination.

        Args:
            source_path: Path to the source file (format depends on provider)
            destination_path: Local path where the file should be available

        Returns:
            Path object pointing to the local file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If file access is denied
        """
        pass

    @abstractmethod
    def put_file(self, source_path: Path, destination_path: str) -> str:
        """Upload a file to storage destination.

        Args:
            source_path: Local file path to upload
            destination_path: Destination path (format depends on provider: local path, s3://, etc.)

        Returns:
            Path/URI to the uploaded file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If upload is denied
        """
        pass

    @abstractmethod
    async def put_file_async(self, source_path: Path, destination_path: str) -> str:
        """Upload a file asynchronously to storage destination.

        Args:
            source_path: Local file path to upload
            destination_path: Destination path (format depends on provider: local path, s3://, etc.)

        Returns:
            Path/URI to the uploaded file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If upload is denied
        """
        pass

    @abstractmethod
    def cleanup(self, path: Path) -> None:
        """Clean up a file that was retrieved by this provider.

        Args:
            path: Path to the file to clean up
        """
        pass

