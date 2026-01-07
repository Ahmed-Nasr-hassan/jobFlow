"""AWS S3 file provider implementation (stub with interface)."""

from pathlib import Path

from ...domain import FileProvider


class S3FileProvider(FileProvider):
    """File provider that accesses files from AWS S3.

    This is a stub implementation that demonstrates the interface.
    In production, this would use boto3 to download files from S3.
    """

    def __init__(self, bucket_name: str | None = None, region: str | None = None) -> None:
        """Initialize the S3 file provider.

        Args:
            bucket_name: Default S3 bucket name (optional)
            region: AWS region (optional)
        """
        self._bucket_name = bucket_name
        self._region = region

    def get_file(self, source_path: str, destination_path: str) -> Path:
        """Retrieve a file from S3.

        Args:
            source_path: S3 path in format 's3://bucket/key' or just 'key' if bucket_name is set
            destination_path: Local path where the file should be available

        Returns:
            Path object pointing to the local file

        Raises:
            FileNotFoundError: If source file cannot be found in S3
            PermissionError: If S3 access is denied

        Note:
            This is a stub implementation. In production, this would:
            1. Parse S3 URI (s3://bucket/key)
            2. Use boto3 to download file
            3. Save to destination_path
            4. Return Path to local file
        """
        raise NotImplementedError(
            "S3FileProvider is a stub. Implement S3 file access by extending this class "
            "or providing a concrete implementation using boto3."
        )

    async def get_file_async(self, source_path: str, destination_path: str) -> Path:
        """Retrieve a file asynchronously from S3.

        Args:
            source_path: S3 path in format 's3://bucket/key' or just 'key' if bucket_name is set
            destination_path: Local path where the file should be available

        Returns:
            Path object pointing to the local file

        Raises:
            FileNotFoundError: If source file cannot be found in S3
            PermissionError: If S3 access is denied

        Note:
            This is a stub implementation. In production, this would:
            1. Parse S3 URI (s3://bucket/key)
            2. Use aioboto3 to download file asynchronously
            3. Save to destination_path
            4. Return Path to local file
        """
        raise NotImplementedError(
            "S3FileProvider is a stub. Implement S3 file access by extending this class "
            "or providing a concrete implementation using aioboto3."
        )

    def put_file(self, source_path: Path, destination_path: str) -> str:
        """Upload a file to S3.

        Args:
            source_path: Local file path to upload
            destination_path: S3 path in format 's3://bucket/key' or just 'key' if bucket_name is set

        Returns:
            S3 URI of the uploaded file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If S3 upload is denied

        Note:
            This is a stub implementation. In production, this would:
            1. Parse S3 URI (s3://bucket/key)
            2. Use boto3 to upload file
            3. Return S3 URI
        """
        raise NotImplementedError(
            "S3FileProvider is a stub. Implement S3 file upload by extending this class "
            "or providing a concrete implementation using boto3."
        )

    async def put_file_async(self, source_path: Path, destination_path: str) -> str:
        """Upload a file asynchronously to S3.

        Args:
            source_path: Local file path to upload
            destination_path: S3 path in format 's3://bucket/key' or just 'key' if bucket_name is set

        Returns:
            S3 URI of the uploaded file

        Raises:
            FileNotFoundError: If source file cannot be found
            PermissionError: If S3 upload is denied

        Note:
            This is a stub implementation. In production, this would:
            1. Parse S3 URI (s3://bucket/key)
            2. Use aioboto3 to upload file asynchronously
            3. Return S3 URI
        """
        raise NotImplementedError(
            "S3FileProvider is a stub. Implement S3 file upload by extending this class "
            "or providing a concrete implementation using aioboto3."
        )

    def cleanup(self, path: Path) -> None:
        """Clean up a file that was retrieved by this provider.

        Args:
            path: Path to the file to clean up
        """
        import os

        try:
            if path.exists():
                if path.is_file():
                    os.remove(path)
                elif path.is_dir():
                    import shutil

                    shutil.rmtree(path)
        except Exception:
            # Silently ignore cleanup errors
            pass

    def _parse_s3_uri(self, source_path: str) -> tuple[str, str]:
        """Parse S3 URI into bucket and key.

        Args:
            source_path: S3 path in format 's3://bucket/key' or just 'key'

        Returns:
            Tuple of (bucket_name, key)
        """
        if source_path.startswith("s3://"):
            # Parse s3://bucket/key format
            parts = source_path[5:].split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
            return bucket, key
        else:
            # Use default bucket if set
            if not self._bucket_name:
                raise ValueError(
                    "S3 bucket name must be provided either in source_path (s3://bucket/key) "
                    "or as bucket_name parameter"
                )
            return self._bucket_name, source_path

