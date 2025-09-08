import asyncio
import inspect
import os
from collections.abc import Awaitable, Callable
from inspect import Parameter
from types import CoroutineType
from typing import Any

from fastmcp import Client, FastMCP
from fastmcp.experimental.sampling.handlers.openai import OpenAI, OpenAISamplingHandler
from fastmcp.server.context import Context
from makefun import wraps
from mcp.types import SamplingMessage, TextContent
from pydantic import BaseModel


class SampleModel(BaseModel):
    name: str
    age: int


"""A Function which takes a Context, any number of additional arguments, and returns an Awaitable
The awaitable returns a string or a tuple of string and the original return value."""


class Summary(BaseModel):
    summary: str


class SummaryResult[T](BaseModel):
    summary: str
    result: T


def offer_summary[**P, R](
    instructions: str,
) -> Callable[..., Callable[..., CoroutineType[Any, Any, R | Summary | SummaryResult[R]]]]:
    """Offer a summary of the function's output."""

    def offer_summary_decorator(func: Callable[P, Awaitable[R]]) -> Callable[..., CoroutineType[Any, Any, R | Summary | SummaryResult[R]]]:
        """Offer a summary of the function's output."""

        @wraps(
            wrapped_fun=func,
            prepend_args=(
                Parameter("context", Parameter.KEYWORD_ONLY, annotation=Context),
                Parameter("summarize", Parameter.KEYWORD_ONLY, annotation=bool, default=False),
                Parameter("include_results", Parameter.KEYWORD_ONLY, annotation=bool, default=False),
            ),
        )
        async def wrapper(
            context: Context,
            summarize: bool = False,
            include_results: bool = False,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R | Summary | SummaryResult[R]:
            response = await func(*args, **kwargs)

            if summarize:
                messages: list[str | SamplingMessage] = [SamplingMessage(role="user", content=TextContent(type="text", text=str(response)))]
                summary = await context.sample(
                    system_prompt=instructions,
                    messages=messages,
                )
                if not isinstance(summary, TextContent):
                    msg = "Summary must be a text content"
                    raise ValueError(msg)

                summary_text = summary.text

                if include_results:
                    return SummaryResult(summary=summary_text, result=response)
                return Summary(summary=summary_text)

            return response

        signature = inspect.signature(wrapper)

        signature = signature.replace(return_annotation=R | Summary | SummaryResult[R])

        wrapper.__signature__ = signature  # pyright: ignore[reportFunctionMemberAccess]

        return wrapper

    return offer_summary_decorator


fastmcp = FastMCP(
    sampling_handler=OpenAISamplingHandler(
        default_model="gemini-2.0-flash",  # pyright: ignore[reportArgumentType]
        client=OpenAI(api_key=os.getenv("GOOGLE_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"),
    )
)


@fastmcp.tool()
@offer_summary(instructions="Please make up a fun (100 words or less) story about the following person")
async def get_person() -> SampleModel:
    return SampleModel(name="John", age=30)


async def main():
    client = Client(fastmcp)
    async with client:
        result = await client.call_tool("get_person", arguments={})
        print("Result:", result)

        result = await client.call_tool("get_person", arguments={"summarize": True, "include_results": False})
        print("Summary:", result)

        result = await client.call_tool("get_person", arguments={"summarize": True, "include_results": True})
        print("Summary and result:", result)


if __name__ == "__main__":
    asyncio.run(main())
