import asyncio
from typing import Literal

import asyncclick as click
from fastmcp import Context, FastMCP
from fastmcp.contrib.mcp_mixin.mcp_mixin import MCPMixin, mcp_tool
from fastmcp.utilities.logging import get_logger
from huggingface_hub import try_to_load_from_cache
from pydantic import BaseModel
from transformers.pipelines import pipeline
from transformers.pipelines.base import Pipeline

logger = get_logger("is-nonsense-mcp")


class IsNonsenseError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ModelNotLoadedError(IsNonsenseError):
    def __init__(self):
        super().__init__("The model has not been loaded. Please call load_model() before using the detector.")


class GibberishScore(BaseModel):
    text: str
    label: str
    score: float


class GibberishDetector(MCPMixin):
    detector: Pipeline | None = None

    def __init__(self):
        super().__init__()
        is_cached = try_to_load_from_cache(
            repo_id="madhurjindal/autonlp-Gibberish-Detector-492513457",
            filename="model.safetensors",
        )  # type: ignore
        if is_cached:
            self.load_model()
        else:
            logger.info("Model not cached, user will need to call load_model() to load the model.")

    @mcp_tool()
    def is_loaded(self) -> bool:
        """Check if the gibberish detector model is already loaded. The server will automatically load
        the model if it is cached locally.

        Returns:
            True if the model is loaded, False otherwise.
        """
        return self.detector is not None

    @mcp_tool()
    def load_model(self):
        """Load the gibberish detector model. Only required the very first time the server is started.

        Will do no harm if the model is already loaded.

        Calling this tool may timeout but the model will continue to be loaded in the background."""
        logger.info("Loading model...")
        self.detector = pipeline("text-classification", model="madhurjindal/autonlp-Gibberish-Detector-492513457")
        logger.info("Model loaded")

    @mcp_tool()
    def detect(self, context: Context, text: str) -> bool:
        """
        Detects gibberish in a text. You must call load_model() before using this tool if this is the first time the server is started.

        Args:
            text: The text to detect gibberish in.

        Returns:
            True if the text is gibberish, False otherwise.
        """
        if self.detector is None:
            raise ModelNotLoadedError

        logger.info(f"Detecting gibberish in {text}")
        result = self.evaluate([text])[0]
        return result.label != "clean"

    @mcp_tool()
    def evaluate(self, texts: list[str]) -> list[GibberishScore]:
        """
        Detects gibberish in a list of texts. You must call load_model() before using this tool if this is the first time the server is started.

        Args:
            texts: A list of texts to detect gibberish in.

        Returns:
            A list of GibberishScore objects which contain the text, label, and score of the gibberish detection.
        """

        if self.detector is None:
            raise ModelNotLoadedError

        logger.info(f"Evaluating {len(texts)} texts")
        results: list[dict[str, str | float]] = self.detector(texts)  # type: ignore

        gibberish_scores = []
        for text, result in zip(texts, results, strict=True):
            if "label" not in result or "score" not in result:
                msg = f"Expected a label and a score, got {result}"
                raise ValueError(msg)

            if not isinstance(result["label"], str) or not isinstance(result["score"], float):
                msg = f"Expected a string and a float, got {type(result['label'])} and {type(result['score'])}"
                raise TypeError(msg)

            label: str = result["label"]
            score: float = result["score"]

            gibberish_scores.append(GibberishScore(text=text, label=label, score=score))

        return gibberish_scores


@click.command()
@click.option(
    "--transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help="The transport to use for the MCP server."
)
async def cli(transport: Literal["stdio", "sse", "streamable-http"]):
    mcp = FastMCP(name="is-nonsense-mcp")

    logger.info("Reticulating splines...")
    gibberish_detector = GibberishDetector()

    gibberish_detector.register_all(mcp)

    logger.info("Spine reticulation complete")

    logger.info("Starting MCP server...")
    await mcp.run_async(transport=transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
