from abc import ABC, abstractmethod

class CloudStorageProvider(ABC):
    @abstractmethod
    async def upload(self, file_path: str, destination_name: str) -> None: ...
    @abstractmethod
    async def download(self, file_key: str, save_path: str) -> None: ...
