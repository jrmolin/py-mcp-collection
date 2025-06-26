from llama_index.core.schema import (
    TransformComponent,
)
from pydantic import Field

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)


class DoclingParentHeading(TransformComponent):
    """Makes a new field called `parent_heading` in the node metadata which is the headings field with the last element removed."""

    parent_heading_key: str = Field(default="parent_headings", description="The key to use for the parent heading.")
    heading_key: str = Field(default="heading", description="The key to use for the heading.")

    def __call__(self, nodes, **kwargs):  # noqa: ARG002
        for node in nodes:
            if "headings" not in node.metadata:
                continue

            headings: list[str] = node.metadata["headings"]

            headings = [heading.split("\n")[0] for heading in headings]

            for i, heading in enumerate(headings):
                headings[i] = "#" * (i + 1) + " " + heading

            parent_headings = headings[:-1]
            if len(parent_headings) > 0:
                node.metadata[self.parent_heading_key] = "\n".join(parent_headings)

            current_heading = headings[-1]
            if current_heading:
                node.metadata[self.heading_key] = current_heading

            node.metadata.pop("headings", None)

        return nodes
