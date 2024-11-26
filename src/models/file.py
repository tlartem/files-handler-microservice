from __future__ import annotations

from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.db_conn import Base

from pydantic import BaseModel
from uuid import UUID


class FileResponseSchema(BaseModel):
    uid: UUID
    original_name: str
    file_size: int
    file_extension: str
    file_format: str


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    original_name: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_format: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_extension: Mapped[str] = mapped_column(String, nullable=False)
