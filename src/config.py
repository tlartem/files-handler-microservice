from pydantic_settings import BaseSettings
from sqlalchemy.orm import DeclarativeBase
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings.
        DATABASE_URL (str): PostgreSQL connection string.
        STORAGE_PATH (str): Path to local file storage.

        AWS_S3_REGION_NAME (str): AWS S3 region name.
        AWS_SECRET_ACCESS_KEY (str): AWS secret access key.
        AWS_ACCESS_KEY_ID (str): AWS access key ID.
        AWS_S3_ENDPOINT_URL (str): URL of the AWS S3 endpoint.
        BUCKET_NAME (str): Name of the S3 bucket.

        BROKER_URL (str): URL of the message broker (e.g., RabbitMQ).
        RESULT_BACKEND (str): Backend URL for task results (e.g., Redis).

        CHUNK_SIZE (int): Default chunk size for file operations in bytes.
        READ_CHUNK_SIZE (int): Chunk size for reading files in bytes.
        WRITE_CHUNK_SIZE (int): Chunk size for writing files in bytes.

        MAX_FILE_SIZE_MB (int): Maximum file size allowed in megabytes.
        ALLOWED_FILE_TYPES (list[str]): List of allowed MIME types for uploaded files.
    """

    # Database
    DATABASE_URL: str
    STORAGE_PATH: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # AWS S3
    AWS_S3_REGION_NAME: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_S3_ENDPOINT_URL: str
    BUCKET_NAME: str

    # Task Queue
    BROKER_URL: str
    RESULT_BACKEND: str

    # Config
    CHUNK_SIZE: int = 1024 * 1024
    READ_CHUNK_SIZE: int = 10 * 1024 * 1024  # 10 MB
    WRITE_CHUNK_SIZE: int = 10 * 1024 * 1024  # 10 MB
    MIN_FREE_SPACE_MB: int = 10 * 1024  # 10 Gb

    # File validator
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: list[str] = ["image/jpeg", "image/png", "application/pdf"]

    # Configuration file
    model_config = ConfigDict(env_file=".env")


settings = Settings()


class Base(DeclarativeBase):
    pass
