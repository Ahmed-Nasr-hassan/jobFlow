"""Local filesystem file provider implementation."""

import shutil
from pathlib import Path

from ...domain import FileProvider


class LocalFileProvider(FileProvider):
    """File provider that accesses files from the local filesystem."""

    def get_file(self, source_path: str, destination_path: str) -> Path:
        """Retrieve a file from local filesystem.

        Args:
            source_path: Local filesystem path to the source file
            destination_path: Local path where the file should be available

        Returns:
            Path object pointing to the local file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If file access is denied
        """
        source = Path(source_path)
        destination = Path(destination_path)

        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Create destination directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Copy file to destination
        if source.is_file():
            shutil.copy2(source, destination)
        elif source.is_dir():
            # For directories, copy the entire directory
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
        else:
            raise ValueError(f"Source path is neither a file nor directory: {source_path}")

        return destination

    async def get_file_async(self, source_path: str, destination_path: str) -> Path:
        """Retrieve a file asynchronously from local filesystem.

        Note: Local filesystem operations are synchronous, but we maintain
        async interface for consistency.

        Args:
            source_path: Local filesystem path to the source file
            destination_path: Local path where the file should be available

        Returns:
            Path object pointing to the local file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If file access is denied
        """
        import asyncio

        # Run synchronous operation in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_file, source_path, destination_path)

    def put_file(self, source_path: Path, destination_path: str) -> str:
        """Copy a file to local filesystem destination.

        Args:
            source_path: Local file path to copy
            destination_path: Local filesystem destination path

        Returns:
            Path to the copied file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If file access is denied
        """
        source = Path(source_path)
        destination = Path(destination_path)

        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Create destination directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Copy file to destination
        if source.is_file():
            shutil.copy2(source, destination)
        elif source.is_dir():
            # For directories, copy the entire directory
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
        else:
            raise ValueError(f"Source path is neither a file nor directory: {source_path}")

        return str(destination)

    async def put_file_async(self, source_path: Path, destination_path: str) -> str:
        """Copy a file asynchronously to local filesystem destination.

        Args:
            source_path: Local file path to copy
            destination_path: Local filesystem destination path

        Returns:
            Path to the copied file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If file access is denied
        """
        import asyncio

        # Run synchronous operation in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.put_file, source_path, destination_path)

    def cleanup(self, path: Path) -> None:
        """Clean up a file that was retrieved by this provider.

        Args:
            path: Path to the file to clean up
        """
        try:
            if path.exists():
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
        except Exception:
            # Silently ignore cleanup errors
            pass

