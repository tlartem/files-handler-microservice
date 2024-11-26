from typing import Protocol


class CloudStorageProvider(Protocol):
    async def upload(self, file_path: str, destination_name: str) -> None:
        """
        Загружает файл в облако.

        :param file_path: Локальный путь к файлу.
        :param destination_name: Имя файла в облаке.
        """
        ...
    async def download(self, file_key: str, save_path: str) -> None:
        ...
