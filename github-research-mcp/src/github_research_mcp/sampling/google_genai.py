from collections.abc import Sequence
from typing import override

from fastmcp.experimental.sampling.handlers.base import BaseLLMSamplingHandler
from google.genai import Client as GoogleGenaiClient
from google.genai.types import (
    Content,
    ContentUnion,
    GenerateContentConfig,
    GenerateContentResponse,
    ModelContent,
    Part,
    UserContent,
)
from mcp import ClientSession, ServerSession
from mcp.shared.context import LifespanContextT, RequestContext
from mcp.types import (
    AudioContent,
    CreateMessageResult,
    ImageContent,
    SamplingMessage,
    TextContent,
)
from mcp.types import CreateMessageRequestParams as SamplingParams


class GoogleGenaiSamplingHandler(BaseLLMSamplingHandler):
    def __init__(self, default_model: str, client: GoogleGenaiClient | None = None):
        self.client: GoogleGenaiClient = client or GoogleGenaiClient()
        self.default_model: str = default_model

    @override
    async def __call__(
        self,
        messages: list[SamplingMessage],
        params: SamplingParams,
        context: RequestContext[ServerSession, LifespanContextT] | RequestContext[ClientSession, LifespanContextT],
    ) -> CreateMessageResult:
        contents: list[ContentUnion] = convert_messages_to_google_genai_content(messages)

        response: GenerateContentResponse = await self.client.aio.models.generate_content(
            model=self.default_model,
            contents=contents,
            config=GenerateContentConfig(
                system_instruction=params.systemPrompt,
                temperature=params.temperature,
                max_output_tokens=params.maxTokens,
                stop_sequences=params.stopSequences,
            ),
        )

        if not (text := response.text):
            msg = "No content in response from completion."
            raise ValueError(msg)

        return CreateMessageResult(
            content=TextContent(type="text", text=text),
            role="assistant",
            model=self.default_model,
        )


def sampling_content_to_google_genai_part(content: TextContent | ImageContent | AudioContent) -> Part:
    if isinstance(content, TextContent):
        return Part(text=content.text)

    msg = f"Invalid content type: {type(content)}"
    raise ValueError(msg)


def convert_messages_to_google_genai_content(
    messages: Sequence[SamplingMessage],
) -> list[ContentUnion]:
    """Convert messages to Gemini messages."""

    google_genai_messages: list[Content] = []

    for message in messages:
        content_part = sampling_content_to_google_genai_part(message.content)

        if message.role == "user":
            google_genai_messages.append(UserContent(parts=[content_part]))

        elif message.role == "assistant":
            google_genai_messages.append(ModelContent(parts=[content_part]))

        else:
            msg = f"Invalid message role: {message.role}"
            raise ValueError(msg)

    return google_genai_messages
