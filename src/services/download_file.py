from __future__ import annotations

import os
from typing import TYPE_CHECKING, Type
from urllib.parse import quote

import aiofiles
from fastapi.responses import StreamingResponse

from src.config import settings
from src.repositories import FileRepository
from src.services.s3 import CloudStorageProvider

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class DownloadFileService:
    def __init__(
        self,
        provider: Type[CloudStorageProvider],
        session: AsyncSession,
    ):
        self.s3_provider = provider()
        self.file_repository = FileRepository(session)

        self.file_record = None
        self.local_file_path = None

    async def get_and_set_file_record(self, uid: str) -> bool:
        self.file_record = await self.file_repository.get_by_uid(uid)
        return True if self.file_record else False

    async def get_file_locally(self) -> bool:
        self.local_file_path = self._get_local_path()
        if not os.path.exists(self.local_file_path):
            try:
                await self.s3_provider.download(
                    file_key=self._get_file_key(),
                    save_path=self.local_file_path,
                )
            except FileNotFoundError:
                return False
        return True

    async def get_file_stream(self) -> StreamingResponse:
        # Асинхронное чтение файла
        async def file_stream(file_path: str):
            async with aiofiles.open(file_path, mode="rb") as file:
                while chunk := await file.read(settings.CHUNK_SIZE):
                    yield chunk

        # Кодировка имени файла для заголовка
        encoded_filename = quote(self.file_record.original_name)

        # Возврат файла через поток
        return StreamingResponse(
            file_stream(self.local_file_path),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            },
        )

    def _get_local_path(self) -> str:
        return os.path.join(
            settings.STORAGE_PATH,
            f"{self.file_record.uid}{self.file_record.file_extension}",
        )

    def _get_file_key(self) -> str:
        return f"{self.file_record.uid}{self.file_record.file_extension}"
