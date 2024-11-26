from __future__ import annotations

import logging
import mimetypes
import os
import uuid
from abc import ABC, abstractmethod
from asyncio import get_running_loop
from dataclasses import dataclass
from typing import Optional, Type

import aiofiles
from starlette.status import HTTP_400_BAD_REQUEST

from src.config import settings

from fastapi import UploadFile, HTTPException


class FileSaveStrategy(ABC):
    @classmethod
    @abstractmethod
    async def save(cls, file: UploadFile, destination: str, file_uid: str) -> str:
        """Сохраняет файл и возвращает путь к нему."""
        pass

    @classmethod
    def _generate_filename(cls, file: UploadFile, file_uid: str) -> str:
        """Генерирует уникальное имя файла."""
        _, file_extension = os.path.splitext(file.filename)
        return f"{file_uid}{file_extension}"


class StreamSave(FileSaveStrategy):
    @classmethod
    async def save(
        cls,
        file: UploadFile,
        destination: str,
        file_uid: str,
    ) -> str:
        unique_filename: str = cls._generate_filename(file, file_uid)
        file_path: str = os.path.join(destination, unique_filename)

        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await file.read(1024):
                await out_file.write(content)

        return file_path


class InMemorySave(FileSaveStrategy):
    @classmethod
    async def save(
        cls,
        file: UploadFile,
        destination: str,
        file_uid: str,
    ) -> str:
        unique_filename: str = cls._generate_filename(file, file_uid)
        file_path: str = os.path.join(destination, unique_filename)

        content: bytes = await file.read()
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(content)

        return file_path


@dataclass
class FileMetadata:
    file_uid: str
    file_unique_name: str
    file_path: str
    file_size: int
    file_extension: str
    file_format: str

    @classmethod
    async def from_upload_file(
        cls,
        file: UploadFile,
        content_length: Optional[str],
    ) -> "FileMetadata":
        if not content_length or int(content_length) > settings.WRITE_CHUNK_SIZE:
            SaveStrategy: Type[FileSaveStrategy] = StreamSave
        else:
            SaveStrategy: Type[FileSaveStrategy] = InMemorySave

        file_uid = str(uuid.uuid4())

        file_path: str = await SaveStrategy.save(
            file, settings.STORAGE_PATH, file_uid=file_uid
        )

        # Получение метаданных
        file_unique_name: str = file_path.split("/")[-1]
        file_size: int = os.path.getsize(file_path)
        file_extension: str = os.path.splitext(file.filename)[1]
        file_format: str = get_format_by_extension(file)

        return cls(
            file_unique_name=file_unique_name,
            file_uid=file_uid,
            file_path=file_path,
            file_size=file_size,
            file_extension=file_extension,
            file_format=file_format,
        )


class FileValidator:
    def __init__(self, allowed_types: list[str], max_size_mb: int):
        self.allowed_types = allowed_types
        self.max_size_mb = max_size_mb

    def validate(self, file: UploadFile) -> None:
        self._validate_size(file)
        self._validate_type(file)

    def _validate_size(self, file: UploadFile) -> None:
        if file.size > self.max_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds the limit of {self.max_size_mb} MB",
            )

    def _validate_type(self, file: UploadFile) -> None:
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(self.allowed_types)}",
            )


def get_format_by_extension(file: UploadFile) -> str:
    file_type, _ = mimetypes.guess_type(file.filename)
    return file_type or "unknown"


async def enough_free_space() -> bool:
    loop = get_running_loop()
    stats = await loop.run_in_executor(None, os.statvfs, "/")
    free_space_mb = (stats.f_bavail * stats.f_frsize) // (1024 * 1024)

    if free_space_mb < settings.MIN_FREE_SPACE_MB:
        logging.warning("Not enough free space to free the file")
        return False

    return True
