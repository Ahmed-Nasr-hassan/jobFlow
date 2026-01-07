"""Composite file provider implementation (routing pattern)."""

from pathlib import Path

from ...domain import FileProvider
from .s3 import S3FileProvider
from .http import HTTPFileProvider


class CompositeFileProvider(FileProvider):
    """Composite file provider that routes file requests to appropriate providers.

    This provider automatically selects the correct FileProvider based on
    the source path format (e.g., s3://, http://, local path).
    """

    def __init__(self, *providers: FileProvider, default_provider: FileProvider | None = None) -> None:
        """Initialize the composite file provider.

        Args:
            *providers: Variable number of file providers to use
            default_provider: Default provider for unrecognized path formats
        """
        self._providers = list(providers)
        self._default_provider = default_provider

    def get_file(self, source_path: str, destination_path: str) -> Path:
        """Retrieve a file using the appropriate provider.

        Args:
            source_path: Path to the source file
            destination_path: Local path where the file should be available

        Returns:
            Path object pointing to the local file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If file access is denied
            ValueError: If no suitable provider is found
        """
        provider = self._select_provider(source_path)
        return provider.get_file(source_path, destination_path)

    async def get_file_async(self, source_path: str, destination_path: str) -> Path:
        """Retrieve a file asynchronously using the appropriate provider.

        Args:
            source_path: Path to the source file
            destination_path: Local path where the file should be available

        Returns:
            Path object pointing to the local file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If file access is denied
            ValueError: If no suitable provider is found
        """
        provider = self._select_provider(source_path)
        return await provider.get_file_async(source_path, destination_path)

    def put_file(self, source_path: Path, destination_path: str) -> str:
        """Upload a file using the appropriate provider.

        Args:
            source_path: Local file path to upload
            destination_path: Destination path (format determines provider)

        Returns:
            Path/URI to the uploaded file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If upload is denied
            ValueError: If no suitable provider is found
        """
        provider = self._select_provider(destination_path)
        return provider.put_file(source_path, destination_path)

    async def put_file_async(self, source_path: Path, destination_path: str) -> str:
        """Upload a file asynchronously using the appropriate provider.

        Args:
            source_path: Local file path to upload
            destination_path: Destination path (format determines provider)

        Returns:
            Path/URI to the uploaded file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If upload is denied
            ValueError: If no suitable provider is found
        """
        provider = self._select_provider(destination_path)
        return await provider.put_file_async(source_path, destination_path)

    def cleanup(self, path: Path) -> None:
        """Clean up a file that was retrieved by this provider.

        Args:
            path: Path to the file to clean up
        """
        # Try all providers to clean up (idempotent operation)
        for provider in self._providers:
            try:
                provider.cleanup(path)
            except Exception:
                pass

        if self._default_provider:
            try:
                self._default_provider.cleanup(path)
            except Exception:
                pass

    def _select_provider(self, source_path: str) -> FileProvider:
        """Select the appropriate provider based on source path format.

        Args:
            source_path: Path to the source file

        Returns:
            Appropriate FileProvider instance

        Raises:
            ValueError: If no suitable provider is found
        """
        # Check for S3 paths
        if source_path.startswith("s3://"):
            for provider in self._providers:
                # Check if it's an S3FileProvider instance
                if isinstance(provider, S3FileProvider) or "S3" in type(provider).__name__:
                    return provider

        # Check for HTTP/HTTPS paths
        if source_path.startswith(("http://", "https://")):
            for provider in self._providers:
                if isinstance(provider, HTTPFileProvider) or "HTTP" in type(provider).__name__:
                    return provider

        # Default to local file provider or default provider
        for provider in self._providers:
            if isinstance(provider, type) and "Local" in provider.__name__:
                return provider
            if hasattr(provider, "get_file") and not hasattr(provider, "_bucket_name"):
                # Assume it's a local provider if it doesn't have S3-specific attributes
                return provider

        # Use default provider if set
        if self._default_provider:
            return self._default_provider

        raise ValueError(f"No suitable file provider found for path: {source_path}")

    def add_provider(self, provider: FileProvider) -> None:
        """Add a file provider to the composite.

        Args:
            provider: File provider to add
        """
        self._providers.append(provider)

