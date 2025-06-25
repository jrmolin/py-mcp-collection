from collections.abc import Sequence

import yaml
from fastmcp.utilities.logging import configure_logging, get_logger
from llama_index.core.schema import BaseNode, Document

NODE_TYPE_MAP = {
    "5": "CHILD",
    "3": "NEXT",
    "4": "PARENT",
    "2": "PREVIOUS",
    "1": "SOURCE",
}

configure_logging(level="INFO")
BASE_LOGGER = get_logger("kb_mcp")

if BASE_LOGGER.parent is not None:
    BASE_LOGGER.parent.propagate = False


def print_node(node: BaseNode):
    printable_node = node.dict()
    # remove nodes I dont care about
    nodes_i_care_about = ["id_", "text", "metadata", "mimetype"]
    printable_node = {k: v for k, v in printable_node.items() if k in nodes_i_care_about}

    metadata_i_care_about = ["headings", "origin"]
    printable_node["metadata"] = {k: v for k, v in printable_node["metadata"].items() if k in metadata_i_care_about}

    # printable_node["relationships"] = new_relationships
    # Grab the first 3 lines of the text
    text = "\n".join(printable_node["text"].splitlines()[:20])
    printable_node["text"] = f"{len(text)} Bytes: {text}..."

    # remove empty values
    printable_node = {k: v for k, v in printable_node.items() if v is not None}
    print(f"-----------------------{printable_node['id_']}-----------------------")
    print(yaml.safe_dump(printable_node, indent=2, sort_keys=False, width=100))


def print_nodes(nodes: Sequence[BaseNode | Document]):
    for node in nodes:
        print_node(node)
