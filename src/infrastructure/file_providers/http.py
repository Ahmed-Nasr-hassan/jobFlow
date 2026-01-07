"""HTTP/HTTPS file provider implementation."""

import asyncio
from pathlib import Path

from ...domain import FileProvider


class HTTPFileProvider(FileProvider):
    """File provider that downloads files from HTTP/HTTPS URLs."""

    def get_file(self, source_path: str, destination_path: str) -> Path:
        """Download a file from HTTP/HTTPS URL.

        Args:
            source_path: HTTP/HTTPS URL to download from
            destination_path: Local path where the file should be saved

        Returns:
            Path object pointing to the downloaded file

        Raises:
            FileNotFoundError: If URL cannot be accessed
            PermissionError: If file access is denied
        """
        import urllib.request
        import urllib.error

        destination = Path(destination_path)

        # Create destination directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Download file from URL
            urllib.request.urlretrieve(source_path, str(destination))
            return destination
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(f"File not found at URL: {source_path}") from e
            raise PermissionError(f"HTTP error {e.code} accessing URL: {source_path}") from e
        except urllib.error.URLError as e:
            raise FileNotFoundError(f"Cannot access URL: {source_path}") from e
        except Exception as e:
            raise FileNotFoundError(f"Failed to download from URL: {source_path}") from e

    async def get_file_async(self, source_path: str, destination_path: str) -> Path:
        """Download a file asynchronously from HTTP/HTTPS URL.

        Args:
            source_path: HTTP/HTTPS URL to download from
            destination_path: Local path where the file should be saved

        Returns:
            Path object pointing to the downloaded file

        Raises:
            FileNotFoundError: If URL cannot be accessed
            PermissionError: If file access is denied
        """
        try:
            import aiohttp
            import aiofiles
        except ImportError:
            # Fallback to synchronous download in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.get_file, source_path, destination_path)

        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source_path) as response:
                    if response.status == 404:
                        raise FileNotFoundError(f"File not found at URL: {source_path}")
                    if response.status >= 400:
                        raise PermissionError(
                            f"HTTP error {response.status} accessing URL: {source_path}"
                        )

                    async with aiofiles.open(destination, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)

            return destination
        except aiohttp.ClientError as e:
            raise FileNotFoundError(f"Cannot access URL: {source_path}") from e
        except Exception as e:
            raise FileNotFoundError(f"Failed to download from URL: {source_path}") from e

    def put_file(self, source_path: Path, destination_path: str) -> str:
        """Upload a file to HTTP/HTTPS endpoint (PUT/POST).

        Args:
            source_path: Local file path to upload
            destination_path: HTTP/HTTPS URL to upload to

        Returns:
            URL of the uploaded file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If upload is denied

        Note:
            This is a basic implementation. For production, you may need
            authentication, multipart uploads, etc.
        """
        import urllib.request
        import urllib.error

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        try:
            with open(source_path, "rb") as f:
                req = urllib.request.Request(
                    destination_path, data=f.read(), method="PUT"
                )
                with urllib.request.urlopen(req) as response:
                    if response.status >= 400:
                        raise PermissionError(
                            f"HTTP error {response.status} uploading to: {destination_path}"
                        )
            return destination_path
        except urllib.error.HTTPError as e:
            raise PermissionError(f"HTTP error {e.code} uploading to: {destination_path}") from e
        except Exception as e:
            raise PermissionError(f"Failed to upload to URL: {destination_path}") from e

    async def put_file_async(self, source_path: Path, destination_path: str) -> str:
        """Upload a file asynchronously to HTTP/HTTPS endpoint.

        Args:
            source_path: Local file path to upload
            destination_path: HTTP/HTTPS URL to upload to

        Returns:
            URL of the uploaded file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If upload is denied
        """
        try:
            import aiohttp
            import aiofiles
        except ImportError:
            # Fallback to synchronous upload in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.put_file, source_path, destination_path)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        try:
            async with aiofiles.open(source_path, "rb") as f:
                file_data = await f.read()

            async with aiohttp.ClientSession() as session:
                async with session.put(destination_path, data=file_data) as response:
                    if response.status >= 400:
                        raise PermissionError(
                            f"HTTP error {response.status} uploading to: {destination_path}"
                        )

            return destination_path
        except aiohttp.ClientError as e:
            raise PermissionError(f"Failed to upload to URL: {destination_path}") from e
        except Exception as e:
            raise PermissionError(f"Failed to upload to URL: {destination_path}") from e

    def cleanup(self, path: Path) -> None:
        """Clean up a file that was retrieved by this provider.

        Args:
            path: Path to the file to clean up
        """
        try:
            if path.exists() and path.is_file():
                path.unlink()
        except Exception:
            # Silently ignore cleanup errors
            pass

