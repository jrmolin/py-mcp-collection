from abc import ABC, abstractmethod


class BaseConvertClient(ABC):
    @abstractmethod
    async def convert(self, content: str) -> str: ...
