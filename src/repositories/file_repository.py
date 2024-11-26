from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import File


class FileRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        original_name: str,
        file_size: int,
        file_extension: str,
        file_uid: str,
        file_format: Optional[str] = None,
    ) -> str:
        try:
            new_file = File(
                uid=file_uid,
                original_name=original_name,
                file_size=file_size,
                file_extension=file_extension,
                file_format=file_format,
            )
            self._session.add(new_file)
            await self._session.commit()
            return file_uid

        except SQLAlchemyError as e:
            await self._session.rollback()
            raise RuntimeError(f"Error occurred while record adding: {e}")

    async def get_by_uid(self, file_uid: str) -> Optional[File]:
        try:
            result = await self._session.execute(
                select(File).where(File.uid == file_uid)
            )
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Error occurred while retrieving file with UID {file_uid}: {e}"
            )

    async def delete_by_uid(self, file_uid: str) -> bool:
        try:
            file = await self.get_by_uid(file_uid)
            if file:
                await self._session.delete(file)
                await self._session.commit()
                return True
            return False

        except SQLAlchemyError as e:
            await self._session.rollback()
            raise RuntimeError(
                f"Error occurred while deleting file with UID {file_uid}: {e}"
            )
