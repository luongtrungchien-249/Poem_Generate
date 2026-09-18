from pathlib import Path


class LocalBlobRepository:
    """Local filesystem blob repository mimicking S3/MinIO."""

    def __init__(self, base_dir: str | None = None) -> None:
        # Thư mục dữ liệu do composition root truyền vào. Không bao giờ ghi cạnh mã nguồn:
        # trong container, site-packages là chỉ đọc.
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "data" / "blobs"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def put_object(self, key: str, data: bytes, content_type: str = "text/plain") -> str:
        safe_key = key.replace("/", "_").replace("\\", "_")
        file_path = self.base_dir / safe_key
        file_path.write_bytes(data)
        return str(file_path)

    async def get_object(self, key: str) -> bytes | None:
        safe_key = key.replace("/", "_").replace("\\", "_")
        file_path = self.base_dir / safe_key
        if file_path.exists():
            return file_path.read_bytes()
        return None

    async def delete_object(self, key: str) -> bool:
        safe_key = key.replace("/", "_").replace("\\", "_")
        file_path = self.base_dir / safe_key
        if file_path.exists():
            file_path.unlink()
            return True
        return False
