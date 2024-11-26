from __future__ import annotations

from fastapi import HTTPException, status


class AppExceptions:
    @staticmethod
    def file_not_found() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    @staticmethod
    def content_length_missing() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_411_LENGTH_REQUIRED,
            detail="Content-Length header is missing",
        )

    @staticmethod
    def invalid_file_data() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file data",
        )

    @staticmethod
    def internal_error() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
