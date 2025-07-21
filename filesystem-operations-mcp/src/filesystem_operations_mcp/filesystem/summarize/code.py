import time
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar, Literal, get_args, override

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.fields import Field
from tree_sitter import Language, Node, Parser, Query, Tree
from tree_sitter_language_pack import (
    SupportedLanguage,
    get_binding,
)

from filesystem_operations_mcp.filesystem.errors import LanguageNotSupportedError
from filesystem_operations_mcp.filesystem.summarize.text import summarizer
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)

TAG_FOLDER = Path(__file__).parent / "tree-sitter-language-pack"
"""A folder of queries that extract significant markers from the corresponding language."""

tag_queries: dict[str, str] = {}

QueryMatch = tuple[int, dict[str, list[Node]]]


def load_tag_queries() -> None:
    """Load all tags for all languages"""
    # Load base tags
    for file in TAG_FOLDER.glob("*-tags.scm"):
        with file.open("r", encoding="utf-8") as f:
            tag_queries[file.stem.replace("-tags", "")] = f.read()

    # load replacement tags
    for file in TAG_FOLDER.glob("*-tags-replace.scm"):
        with file.open("r", encoding="utf-8") as f:
            tag_queries[file.stem.replace("-tags-replace", "")] = f.read()

    # Load extra tags
    for file in TAG_FOLDER.glob("*-tags-extra.scm"):
        with file.open("r", encoding="utf-8") as f:
            # File without `extra` suffix
            tag_queries[file.stem.replace("-tags-extra", "")] += "\n" + f.read()


def ensure_initialized() -> None:
    if not tag_queries:
        load_tag_queries()


def to_supported_language(language_name: str) -> SupportedLanguage:
    if language_name not in get_args(SupportedLanguage):
        raise LanguageNotSupportedError(language=language_name)

    supported_language: Literal[SupportedLanguage] = language_name  # pyright: ignore[reportAssignmentType]

    return supported_language


def get_language(language_name: str) -> Language:
    supported_language: SupportedLanguage = to_supported_language(language_name=language_name)

    binding = get_binding(language_name=supported_language)

    return Language(binding)


@lru_cache(maxsize=30)
def get_language_parser(language: Language) -> Parser:
    parser: Parser = Parser(language=language)

    return parser


class ViewNode(BaseModel):
    """A view of a node in the AST."""

    ast_id: int = Field(exclude=True)
    ast_node: Node = Field(exclude=True)
    identifier: str
    is_root_node: bool = Field(default=False, exclude=True)
    doc_nodes: list[Node] = Field(exclude=True)
    child_nodes: dict[str, list["ViewNode"]] = Field(default_factory=dict, exclude=True)

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    @override
    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any] | str | None:  # pyright: ignore[reportAny, reportIncompatibleMethodOverride]
        result = super().model_dump(*args, **kwargs)

        for key, children in self.child_nodes.items():
            result[key] = [child.model_dump(*args, **kwargs) for child in children]

        if len(result) == 1 and "identifier" in result:
            return result["identifier"]  # pyright: ignore[reportAny]
        if len(result) > 1:
            return result

        return result

    @computed_field
    def docs(self) -> str | None:
        if self.is_root_node:
            return None

        docs = [
            doc_node.text.decode("utf-8").strip("/'# ")
            for doc_node in self.doc_nodes  # linter is wrong
            if doc_node.text is not None
        ]

        if not docs:
            return None

        summary = summarizer.summarize(document="\n".join(docs))

        if summary == "":
            return None

        return summary


def new_pruned_tree(node: Node, interesting_nodes: list[Node], doc_nodes: list[Node]) -> ViewNode:
    """Produce a pruned tree of the interesting nodes.

    A pruned tree has a root node and branches, the branches are only interesting nodes and their children.
    We return ViewNode objects for each node.
    """
    root_node = ViewNode(ast_id=node.id, ast_node=node, identifier=node.type, is_root_node=True, doc_nodes=[])

    _ = prune_branches(root_node, node, interesting_nodes, doc_nodes)

    return root_node


def prune_branches(last_interesting_node_view: ViewNode, node: Node, interesting_nodes: list[Node], doc_nodes: list[Node]) -> ViewNode:
    """Deep-first search of the tree, returning a ViewNode object for each interesting node, linked to the most recent
    interesting node in the depth-first search.

    Whether or not we are an interesting node, we need to continue depth first to see if we have any descendants that are interesting.

    If we are an interesting node, we continue the search but we become the parent_view_node
    """

    view_node = last_interesting_node_view

    if node in interesting_nodes:
        # Search for any child "identifier" nodes and use them for our identifier
        identifier_child = next((child for child in node.children if child.grammar_name == "identifier"), None)
        identifier = (
            identifier_child.text.decode("utf-8")
            if identifier_child is not None and identifier_child.text is not None
            else node.type  # linter is wrong
        )

        view_node = ViewNode(ast_id=node.id, ast_node=node, identifier=identifier, is_root_node=False, doc_nodes=[])

        # Check for preceeding comments
        if node not in doc_nodes:
            last_interesting_node_view.child_nodes.setdefault(node.type, []).append(view_node)

            previous_sibling: Node | None = node.prev_sibling

            while previous_sibling is not None and previous_sibling.grammar_name == "comment" and previous_sibling in doc_nodes:
                view_node.doc_nodes.append(previous_sibling)
                previous_sibling = previous_sibling.prev_sibling

            for doc_node in view_node.doc_nodes:
                if doc_node in doc_nodes:
                    doc_nodes.remove(doc_node)

        if node in doc_nodes:
            last_interesting_node_view.doc_nodes.append(node)

    for child in node.children:
        _ = prune_branches(view_node, child, interesting_nodes, doc_nodes)

    return view_node


def summarize_code(language_name: str, code: str) -> dict[str, Any] | str | None:
    timers: dict[str, float] = {
        "start": time.time(),
    }

    ensure_initialized()

    timers["ensure_initialized"] = time.time()

    if language_name not in tag_queries:
        return None

    # Get the language and parser
    language: Language = get_language(language_name=language_name)

    timers["get_language"] = time.time()

    parser: Parser = get_language_parser(language=language)

    timers["get_language_parser"] = time.time()

    # Parse the code
    tree: Tree = parser.parse(code.encode())

    timers["parse"] = time.time()

    # Identify the tags
    tag_query: Query = language.query(tag_queries[language_name])
    if not hasattr(tag_query, "captures"):
        logger.debug(f"Tag query for {language_name} does not have captures. Skipping file.")
        return None

    captures: dict[str, list[Node]] = tag_query.captures(tree.root_node)

    timers["tag_query_captures"] = time.time()

    interesting_captures = {
        key: captures[key]
        for key in captures  # linter is wrong
        if key.startswith(("definition", "doc"))
    }

    interesting_nodes = [node for nodes in interesting_captures.values() for node in nodes]

    doc_captures = {
        key: captures[key]
        for key in captures  # linter is wrong
        if key.startswith("doc")
    }

    doc_nodes = [node for nodes in doc_captures.values() for node in nodes]

    timers["interesting_nodes"] = time.time()

    summary_model_view = new_pruned_tree(
        node=tree.root_node,
        interesting_nodes=interesting_nodes,
        doc_nodes=doc_nodes,
    )

    timers["new_pruned_tree"] = time.time()

    if summary_model_view is None:  # pyright: ignore[reportUnnecessaryComparison]
        return None

    dumped_model = summary_model_view.model_dump(exclude_none=True, exclude_defaults=True, mode="json")

    timers["dumped_model"] = time.time()

    times: dict[str, float] = {
        "ensure_initialized": timers["ensure_initialized"] - timers["start"],
        "get_language": timers["get_language"] - timers["ensure_initialized"],
        "get_language_parser": timers["get_language_parser"] - timers["get_language"],
        "parse": timers["parse"] - timers["get_language_parser"],
        "tag_query_captures": timers["tag_query_captures"] - timers["parse"],
        "interesting_nodes": timers["interesting_nodes"] - timers["tag_query_captures"],
        "new_pruned_tree": timers["new_pruned_tree"] - timers["interesting_nodes"],
        "dumped_model": timers["dumped_model"] - timers["new_pruned_tree"],
        "total": timers["dumped_model"] - timers["start"],
    }

    logger.info(f"Summarize code took: {times}")

    return dumped_model
