from abc import ABC, abstractmethod


class BaseFetchClient(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> str: ...
