"""Storage backend abstraction — local filesystem and S3-compatible."""

import os
from abc import ABC, abstractmethod
from pathlib import Path

import structlog

logger = structlog.get_logger()


class StorageBackend(ABC):
    """Abstract storage interface.

    Implementations must support put, get, delete, and url operations.
    This allows swapping local dev storage for S3 in production
    without changing business logic.
    """

    @abstractmethod
    async def put(self, path: str, data: bytes) -> str:
        """Store data at the given path. Returns the storage path."""
        ...

    @abstractmethod
    async def get(self, path: str) -> bytes:
        """Retrieve data from the given path."""
        ...

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete data at the given path."""
        ...

    @abstractmethod
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get a URL for accessing the stored file (signed URL for S3)."""
        ...


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage for development."""

    def __init__(self, base_path: str = "./uploads") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def put(self, path: str, data: bytes) -> str:
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)
        logger.debug("file_stored_locally", path=path, size=len(data))
        return path

    async def get(self, path: str) -> bytes:
        full_path = self.base_path / path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return full_path.read_bytes()

    async def delete(self, path: str) -> None:
        full_path = self.base_path / path
        if full_path.exists():
            full_path.unlink()
            logger.debug("file_deleted_locally", path=path)

    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        # In local dev, return a file path (not a real URL)
        return f"/uploads/{path}"


class S3StorageBackend(StorageBackend):
    """S3-compatible storage backend for production."""

    def __init__(
        self,
        bucket: str,
        endpoint: str | None = None,
        region: str = "us-east-1",
    ) -> None:
        import boto3

        kwargs: dict = {"region_name": region}
        if endpoint:
            kwargs["endpoint_url"] = endpoint

        self.s3 = boto3.client("s3", **kwargs)
        self.bucket = bucket

    async def put(self, path: str, data: bytes) -> str:
        self.s3.put_object(Bucket=self.bucket, Key=path, Body=data)
        logger.debug("file_stored_s3", path=path, bucket=self.bucket, size=len(data))
        return path

    async def get(self, path: str) -> bytes:
        response = self.s3.get_object(Bucket=self.bucket, Key=path)
        return response["Body"].read()

    async def delete(self, path: str) -> None:
        self.s3.delete_object(Bucket=self.bucket, Key=path)
        logger.debug("file_deleted_s3", path=path, bucket=self.bucket)

    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": path},
            ExpiresIn=expires_in,
        )


# ----- Factory -----

_storage_instance: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Get the configured storage backend singleton."""
    global _storage_instance
    if _storage_instance is None:
        from app.config import settings

        if settings.storage_backend == "s3":
            _storage_instance = S3StorageBackend(
                bucket=settings.s3_bucket,
                endpoint=settings.s3_endpoint or None,
                region=settings.s3_region,
            )
        else:
            _storage_instance = LocalStorageBackend(settings.local_storage_path)
        logger.info("storage_initialized", backend=settings.storage_backend)
    return _storage_instance
