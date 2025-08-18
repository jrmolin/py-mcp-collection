from typing import override

from html_to_markdown import convert_to_markdown

from web_search_summary_mcp.clients.convert.base import BaseConvertClient


class MarkdownConvertClient(BaseConvertClient):
    @override
    async def convert(self, content: str) -> str:
        return convert_to_markdown(source=content, preprocess_html=True)
