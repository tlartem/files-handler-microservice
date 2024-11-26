import asyncio
from typing import Type

from src.services.s3 import YandexCloudProvider, CloudStorageProvider
from src.tasks.celery_app import app as celery


@celery.task(name="upload_file_to_cloud")
def upload_file_to_cloud(*args, **kwargs):
    asyncio.run(_upload_file_to_cloud(*args, **kwargs))


async def _upload_file_to_cloud(file_path: str, destination_name: str) -> None:
    provider = YandexCloudProvider()
    await provider.upload(destination_name, file_path)
