from collections.abc import Sequence

from llama_index.core.schema import (
    BaseNode,
    MetadataMode,
    TransformComponent,
)
from pydantic import Field

from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.window import PeekableWindow

logger = BASE_LOGGER.getChild(__name__)

CODE_BLOCK_LABEL = "code"
TABLE_BLOCK_LABEL = "table"
TEXT_LABEL = "text"


def check_metadata_matching(nodes: list[BaseNode], metadata_matching: list[str]) -> bool:
    """Checks if the node's metadata matches the metadata matching."""
    reference_node = nodes[0]

    return all(all(node.metadata.get(key) == reference_node.metadata.get(key) for key in metadata_matching) for node in nodes)


def analyze_window(nodes: Sequence[BaseNode]) -> tuple[list[BaseNode], list[BaseNode], list[BaseNode], list[BaseNode]]:
    """Analyzes a window of nodes and returns a dictionary of node types."""
    text_nodes: list[BaseNode] = [node for node in nodes if node.metadata.get("docling_item_label") == TEXT_LABEL]
    code_nodes: list[BaseNode] = [node for node in nodes if node.metadata.get("docling_item_label") == CODE_BLOCK_LABEL]
    table_nodes: list[BaseNode] = [node for node in nodes if node.metadata.get("docling_item_label") == TABLE_BLOCK_LABEL]
    other_nodes: list[BaseNode] = [
        node for node in nodes if node.metadata.get("docling_item_label") not in [TEXT_LABEL, CODE_BLOCK_LABEL, TABLE_BLOCK_LABEL]
    ]

    return text_nodes, code_nodes, table_nodes, other_nodes


class DoclingSubsequentCodeBlockOrTable(TransformComponent):
    """Merges subsequent code blocks or tables into the previous node's metadata and excludes it from the node's embeddings."""

    metadata_matching: list[str] = Field(default_factory=list, description="The metadata keys which must match for nodes to be merged.")

    def __call__(self, nodes, **kwargs):  # noqa: ARG002
        new_nodes: list[BaseNode] = []

        for window in PeekableWindow[BaseNode](items=nodes):
            reference_node = window.look_one()

            while peek_node := window.peek_right():
                if reference_node.metadata.get("heading") == "### model_extra":
                    pass

                if not check_metadata_matching(nodes=[reference_node, peek_node], metadata_matching=self.metadata_matching):
                    break

                peek_left_nodes, peek_right_nodes = window.peek()
                peek_nodes = [*peek_left_nodes, *peek_right_nodes, *window.look()]

                text_nodes, code_nodes, table_nodes, other_nodes = analyze_window(nodes=peek_nodes)

                if len(other_nodes) > 0:
                    break

                if len(text_nodes) > 1:
                    break

                if len(text_nodes) == 1:
                    window.grow_to_peek()

            nodes_in_window = window.look()

            if len(nodes_in_window) == 1:
                new_nodes.append(reference_node)
                continue

            text_nodes, code_nodes, table_nodes, other_nodes = analyze_window(nodes=nodes_in_window)

            text_node = text_nodes[0]

            code_node_contents: str = "\n".join([node.get_content(metadata_mode=MetadataMode.NONE) for node in code_nodes])
            table_node_contents: str = "\n".join([node.get_content(metadata_mode=MetadataMode.NONE) for node in table_nodes])

            if len(code_nodes) > 0:
                text_node.metadata["example_code_block"] = code_node_contents
                text_node.excluded_embed_metadata_keys.append("example_code_block")

            if len(table_nodes) > 0:
                text_node.metadata["example_table"] = table_node_contents
                text_node.excluded_embed_metadata_keys.append("example_table")

            new_nodes.append(text_node)

            # node_label = node.metadata.get("docling_item_label")

            # if node_label not in node_types:
            #     continue

            # while peek_node := window.peek_right():
            #     peek_node_is_code_block_or_table = peek_node.metadata.get("docling_item_label") in [CODE_BLOCK_LABEL, TABLE_BLOCK_LABEL]

            #     # If both are code blocks or tables, we can stop
            #     if node_is_code_block_or_table and peek_node_is_code_block_or_table:
            #         break

            #     # If neither are code blocks or tables, we can stop
            #     if not (node_is_code_block_or_table or peek_node_is_code_block_or_table):
            #         break

            #     peek_node_metadata = {
            #         key: peek_node.metadata[key] for key in self.metadata_matching if peek_node.metadata.get(key) is not None
            #     }

            #     if node_metadata != peek_node_metadata:
            #         break

            #     winner_node = peek_node if node_is_code_block_or_table else node
            #     loser_node = node if node_is_code_block_or_table else peek_node

            #     loser_node_label = loser_node.metadata.get("docling_item_label")
            #     loser_node_content = loser_node.get_content(metadata_mode=MetadataMode.NONE)

            #     node_metadata_key = "example_code_block" if loser_node_label == CODE_BLOCK_LABEL else "example_table"

            #     winner_node.metadata[node_metadata_key] = loser_node_content
            #     winner_node.excluded_embed_metadata_keys.append(node_metadata_key)

            #     node = winner_node

            #     window.grow_to_peek()
            #     break

            # new_nodes.append(node)

        return new_nodes
