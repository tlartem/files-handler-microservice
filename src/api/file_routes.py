from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import StreamingResponse

from src import tasks
from src.config import settings
from src.db_conn import get_session
from src.models import AppExceptions, File, FileResponseSchema
from src.repositories import FileRepository
from src.services import DownloadFileService, UploadFileService, enough_free_space
from src.services.proceed_file import FileMetadata, FileValidator
from src.services.s3 import YandexCloudProvider

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка файла",
)
async def upload_file(
    request: Request,
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Загрузка файла.

    Загружает файл на сервер, выполняет его проверку на допустимость и отправляет в облачное хранилище.

    - **file**: файл, который нужно загрузить.

    Возвращает:
    - **uid**: уникальный идентификатор файла.
    """
    if not await enough_free_space():
        raise AppExceptions.internal_error()

    FileValidator(
        allowed_types=settings.ALLOWED_FILE_TYPES,
        max_size_mb=settings.MAX_FILE_SIZE_MB,
    ).validate(file)

    file_metadata: FileMetadata = await UploadFileService.proceed_file(
        file, request, session
    )

    # Таска для Celery
    tasks.upload_file_to_cloud.delay(
        file_path=file_metadata.file_path,
        destination_name=file_metadata.file_unique_name,
    )

    return {"uid": file_metadata.file_uid}


@router.get("/{uid}", status_code=status.HTTP_200_OK)
async def get_file(
    uid: UUID,
    session: AsyncSession = Depends(get_session),
) -> FileResponseSchema:
    """
    Получает информацию о файле по UID.

    - **uid**: Уникальный идентификатор файла.

    Возвращает:
    - Детали файла (оригинальное имя, размер, расширение и формат).
    """
    # Получаем запись о файле из базы
    file_record: Optional[File] = await FileRepository(session).get_by_uid(str(uid))

    if not file_record:
        raise AppExceptions.file_not_found()

    return FileResponseSchema(
        uid=file_record.uid,
        original_name=file_record.original_name,
        file_size=file_record.file_size,
        file_extension=file_record.file_extension,
        file_format=file_record.file_format or "unknown",
    )


@router.get("/download/{uid}", status_code=status.HTTP_200_OK)
async def download_file(
    uid: str,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """
    Скачивает файл по UID.

    - **uid**: Уникальный идентификатор файла.

    Возвращает:
    - Потоковый ответ с содержимым файла.
    """

    download_service = DownloadFileService(YandexCloudProvider, session)

    if not await download_service.get_and_set_file_record(uid):
        raise AppExceptions.file_not_found()

    if not await download_service.get_file_locally():
        raise AppExceptions.file_not_found()

    file_stream: StreamingResponse = await download_service.get_file_stream()

    return file_stream
