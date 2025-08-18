from typing import override

from aiohttp import ClientSession

from web_search_summary_mcp.clients.fetch.base import BaseFetchClient


class SimpleFetchClient(BaseFetchClient):
    session: ClientSession | None

    def __init__(self, session: ClientSession | None = None):
        self.session = session

    @override
    async def fetch(self, url: str) -> str:
        if self.session is None:
            self.session = ClientSession()

        async with self.session.get(url) as response:
            response.raise_for_status()

            return await response.text()
