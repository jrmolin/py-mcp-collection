# pyright: reportAny=false,reportExplicitAny=false

from collections import OrderedDict
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import pytest
import yaml
from llama_index.core.schema import BaseNode, Document, MediaResource, MetadataMode, TextNode
from pydantic import BaseModel, Field
from syrupy.assertion import SnapshotAssertion

from knowledge_base_mcp.utils.patches import apply_patches
from tests.extensions.markdown_snapshot_extension import MarkdownSnapshotExtension
from tests.extensions.yaml_snapshot_extension import YAMLSnapshotExtension

apply_patches()


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.with_defaults()


@pytest.fixture
def yaml_snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.with_defaults(extension_class=YAMLSnapshotExtension)


@pytest.fixture
def text_snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.with_defaults(extension_class=MarkdownSnapshotExtension)


def validate_relationships(nodes: Sequence[BaseNode]) -> None:
    """Validate the relationships of the nodes."""
    nodes_by_id: dict[str, BaseNode] = {node.node_id: node for node in nodes}

    for node in nodes:
        if node.child_nodes is not None:
            for child_node in node.child_nodes:
                assert child_node.node_id in nodes_by_id, f"Child node {child_node.node_id} not found in nodes_by_id"
        if node.parent_node:
            assert node.parent_node.node_id in nodes_by_id, f"Parent node {node.parent_node.node_id} not found in nodes_by_id"
        if node.prev_node:
            assert node.prev_node.node_id in nodes_by_id, f"Previous node {node.prev_node.node_id} not found in nodes_by_id"
        if node.next_node:
            assert node.next_node.node_id in nodes_by_id, f"Next node {node.next_node.node_id} not found in nodes_by_id"


@pytest.fixture
def text_node():
    """Factory fixture for creating TextNode from markdown string."""

    def _make(markdown: str) -> TextNode:
        return TextNode(text=markdown)

    return _make


def get_sample_simple_markdown_str() -> str:
    """Get a sample string from a simple markdown document."""

    source: Path = Path("tests/samples/simple_document.md")

    return source.read_text()


def get_sample_simple_markdown_document() -> Document:
    """Get a sample document from a simple markdown document."""
    return Document(text=get_sample_simple_markdown_str(), metadata={"file_name": "simple_document.md"})


def get_sample_pydantic_models_html_str() -> str:
    """Get a sample string from the pydantic models documentation."""
    source: Path = Path("tests/samples/pydantic_models.html")

    return source.read_text()


def get_sample_pydantic_models_html_document() -> Document:
    """Get a sample document from the pydantic models documentation."""
    return Document(text=get_sample_pydantic_models_html_str(), metadata={"file_name": "pydantic_models.html"})


def no_isolated_nodes(nodes: Sequence[BaseNode]) -> bool:
    """Check if the nodes have isolated nodes."""
    isolated_nodes: list[BaseNode] = [node for node in nodes if node.parent_node is None and node.child_nodes is None]
    return len(isolated_nodes) == 0


def leaf_nodes_have_siblings(nodes: Sequence[BaseNode]) -> bool:
    """Check if the leaf nodes have siblings."""
    leaf_nodes: list[BaseNode] = [node for node in nodes if node.child_nodes is None]
    leaf_nodes_without_siblings: list[BaseNode] = [node for node in leaf_nodes if node.next_node is None and node.prev_node is None]
    return len(leaf_nodes_without_siblings) == 0


def has_embeddings(nodes: Sequence[BaseNode]) -> bool:
    """Check if the nodes have embeddings."""
    return all(node.embedding is None for node in nodes)


def join_content(nodes: Sequence[BaseNode]) -> str:
    return ("\n\n".join([node.get_content(metadata_mode=MetadataMode.NONE) for node in nodes])).strip()


def assert_no_isolated_nodes(nodes: Sequence[BaseNode]) -> None:
    """Assert that the nodes have no isolated nodes."""
    assert no_isolated_nodes(nodes=nodes)


def truncate_text(text: str, length: int = 150) -> str:
    """Truncate the text to 1000 characters."""
    return (text[:length] + "...") if len(text) > length else text


def organize_nodes_for_snapshot(nodes: Sequence[BaseNode], extra_nodes: Sequence[BaseNode] | None = None) -> list[dict[str, Any]]:
    """Organize the nodes for snapshot."""
    serialized_nodes: list[dict[str, Any]] = serialize_nodes_for_snapshot(nodes=nodes, extra_nodes=extra_nodes)
    serialized_nodes_by_id: dict[str, dict[str, Any]] = {node["node_id"]: node for node in serialized_nodes}

    root_nodes: list[dict[str, Any]] = [
        node for node in serialized_nodes if node["relationships"].get("parent") not in serialized_nodes_by_id
    ]

    for node in serialized_nodes:
        if not (relationships := node.get("relationships")):
            continue

        members: Sequence[dict[str, Any]] = []

        for child_id in relationships.get("children", []):
            if not (child := serialized_nodes_by_id.get(child_id)):
                continue

            members.append(child)

        node["members"] = members

    return root_nodes


def serialize_node_structure_for_snapshot(nodes: Sequence[BaseNode], extra_nodes: Sequence[BaseNode] | None = None) -> str:
    """Serialize the node structure for snapshot."""
    serialized_nodes: list[dict[str, Any]] = serialize_nodes_for_snapshot(nodes=nodes, extra_nodes=extra_nodes)

    structure: list[str] = []

    for node in serialized_nodes:
        content: str = node["content"]
        content_preview: str = content[:50].replace("\n", " ")
        structure.append(f"{'  ' * node['node_depth']} : {node['node_id']} - {node['content_length']}: {content_preview}")

    return "\n".join(structure)


def serialize_nodes_for_snapshot(nodes: Sequence[BaseNode], extra_nodes: Sequence[BaseNode] | None = None) -> list[dict[str, Any]]:
    """Serialize the nodes for snapshot.

    Args:
        nodes: The nodes to serialize.
        extra_nodes: Extra nodes to not include in the snapshot but allow references to.

    Returns:
        The serialized nodes.
    """
    if extra_nodes is None:
        extra_nodes = []

    serialized_nodes: list[dict[str, Any]] = []
    nodes_by_id: dict[str, BaseNode] = {node.node_id: node for node in nodes}
    guid_to_friendly_id: dict[str, str] = {}

    for i, node in enumerate([*nodes, *extra_nodes]):
        # Check if it's a GUID or a string
        if len(node.node_id) == 36:
            guid_to_friendly_id[node.node_id] = str(i)
        else:
            guid_to_friendly_id[node.node_id] = node.node_id

    def determine_node_depth(node_id: str, depth: int = 0) -> int:
        if node_id in nodes_by_id:
            node: BaseNode = nodes_by_id[node_id]
            if node.parent_node:
                return determine_node_depth(node_id=node.parent_node.node_id, depth=depth + 1)
            return depth
        return depth

    for node in nodes:
        content = node.get_content()

        serialized_node: OrderedDict[str, Any] = OrderedDict(
            {
                "node_id": guid_to_friendly_id[node.node_id],
                "node_depth": determine_node_depth(node_id=node.node_id),
                "node_type": node.__class__.__name__,
                "content_length": len(content),
                "content": truncate_text(text=content, length=1000),
            }
        )

        serialized_node["metadata"] = {key: truncate_text(text=value, length=100) for key, value in node.metadata.items()}

        serialized_node["metadata_llm"] = {
            key: value for key, value in serialized_node["metadata"].items() if key not in node.excluded_llm_metadata_keys
        }

        serialized_node["metadata_embed"] = {
            key: value for key, value in serialized_node["metadata"].items() if key not in node.excluded_embed_metadata_keys
        }

        if serialized_node["metadata_llm"] == serialized_node["metadata"]:
            del serialized_node["metadata_llm"]
        if serialized_node["metadata_embed"] == serialized_node["metadata"]:
            del serialized_node["metadata_embed"]

        if is_isolated := node.parent_node is None and node.child_nodes is None:
            serialized_node["is_isolated"] = is_isolated

        relationships = {}
        if node.parent_node:
            relationships["parent"] = guid_to_friendly_id[node.parent_node.node_id]
        if node.prev_node:
            relationships["previous"] = guid_to_friendly_id[node.prev_node.node_id]
        if node.next_node:
            relationships["next"] = guid_to_friendly_id[node.next_node.node_id]
        if node.child_nodes:
            relationships["children"] = [guid_to_friendly_id[child_node.node_id] for child_node in node.child_nodes]

        serialized_node["relationships"] = relationships

        serialized_node = OrderedDict({k: v for k, v in serialized_node.items() if v is not None or v in ({}, [])})

        serialized_nodes.append(serialized_node)

    return serialized_nodes


class SampleNode(BaseModel):
    type: Literal["root", "group", "node"]
    metadata: dict[str, Any] = Field(default_factory=dict)
    content: str


class Sample(BaseModel):
    directory: Path = Field(description="The directory of the sample.", exclude=True)

    @property
    def name(self) -> str:
        return self.directory.name

    @property
    def description(self) -> Path:
        return next(self.directory.glob(pattern="readme.md"))

    @property
    def input_file(self) -> Path:
        return next(self.directory.glob(pattern="input.*"))

    @property
    def input_type(self) -> Literal["text/html", "text/markdown"]:
        match self.input_file.suffix.lstrip("."):
            case "md":
                return "text/markdown"
            case "html":
                return "text/html"
            case _:
                msg = f"Invalid input file type: {self.input_file.suffix}"
                raise ValueError(msg)

    @property
    def input_text(self) -> str:
        return self.input_file.read_text()

    def input_as_document(self) -> Document:
        text_resource: MediaResource = MediaResource(text=self.input_text, mimetype=self.input_type)
        document: Document = Document(text_resource=text_resource)

        return document

    def cases(self) -> list[str]:
        # any directories in the sample directory are cases
        return [directory.name for directory in self.directory.iterdir() if directory.is_dir()]

    def get_case(self, case: str) -> list[SampleNode]:
        case_dir: Path = self.directory / case
        case_nodes_yml: Path = case_dir / "nodes.yml"
        return [SampleNode(**node) for node in yaml.safe_load(case_nodes_yml.read_text())]


class DoclingSample(Sample):
    def nodes(self) -> list[SampleNode]:
        return self.get_case(case="docling")

    @classmethod
    def from_sample(cls, sample: Sample) -> "DoclingSample":
        return cls(directory=sample.directory)


def get_sample(sample_type: Literal["html", "markdown"], name: str) -> Sample:
    """Get a sample from the samples directory."""
    sample_dir: Path = Path(f"tests/samples/{sample_type}/{name}")
    if not sample_dir.exists():
        msg = f"Sample directory not found: {sample_dir}"
        raise FileNotFoundError(msg)

    return Sample(directory=sample_dir)


def get_docling_sample(sample_type: Literal["html", "markdown"], name: str) -> DoclingSample:
    sample: Sample = get_sample(sample_type=sample_type, name=name)
    return DoclingSample.from_sample(sample=sample)


def get_docling_samples(sample_type: Literal["html", "markdown"]) -> list[DoclingSample]:
    """Get a list of docling samples from the samples directory."""
    return [get_docling_sample(sample_type=sample_type, name=sample.name) for sample in get_samples(sample_type=sample_type)]


def get_samples(sample_type: Literal["html", "markdown"]) -> list[Sample]:
    """Get a list of samples from the samples directory."""
    sample_dir: Path = Path(f"tests/samples/{sample_type}")
    if not sample_dir.exists():
        msg = f"Sample directory not found: {sample_dir}"
        raise FileNotFoundError(msg)

    return [Sample(directory=sample_dir) for sample_dir in sample_dir.iterdir()]


# def to_llama_document(mimetype: Literal["text/html", "text/markdown"], text: str) -> Document:
#     text_resource: MediaResource = MediaResource(text=text, mimetype=mimetype)
#     return Document(text_resource=text_resource)
