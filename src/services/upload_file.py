from fastapi import UploadFile, Request, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models import AppExceptions
from src.repositories import FileRepository
from src.services import FileMetadata


class UploadFileService:
    @staticmethod
    async def proceed_file(
        file: UploadFile, request: Request, session: AsyncSession
    ) -> FileMetadata:
        # Проверяем наличие заголовка Content-Length
        content_length = request.headers.get("content-length")
        if not content_length:
            raise AppExceptions.content_length_missing()

        try:
            # Генерируем метаданные файла
            file_metadata = await FileMetadata.from_upload_file(
                file=file,
                content_length=content_length,
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File metadata generate error",
            )

        try:
            # Сохраняем метаданные файла в базе данных
            await FileRepository(session).create(
                original_name=file.filename,
                file_size=file_metadata.file_size,
                file_extension=file_metadata.file_extension,
                file_uid=file_metadata.file_uid,
                file_format=file_metadata.file_format,
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return file_metadata
