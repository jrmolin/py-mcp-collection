from collections import defaultdict
from collections.abc import Sequence
from logging import Logger
from typing import override

from llama_index.core.bridge.pydantic import Field
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import (
    BaseNode,
    MediaResource,
    MetadataMode,
    Node,
    NodeRelationship,
    NodeWithScore,
    QueryBundle,
)
from llama_index.core.storage.docstore.types import BaseDocumentStore

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


def get_type_from_node(node: BaseNode) -> str:
    """Get the type from a node."""

    if type := node.metadata.get("type"):
        if not isinstance(type, str):
            msg = f"Type is not a string: {type}"
            raise TypeError(msg)

        return type

    msg = f"Type is not found in the node metadata: {node.metadata}"
    raise ValueError(msg)


def get_repository_from_node(node: BaseNode) -> str:
    """Get the repository from a node."""

    if repository := node.metadata.get("repository"):
        if not isinstance(repository, str):
            msg = f"Repository is not a string: {repository}"
            raise TypeError(msg)

        return repository

    msg = f"Repository is not found in the node metadata: {node.metadata}"
    raise ValueError(msg)


def get_issue_from_node(node: BaseNode) -> int:
    """Get the issue from a node."""

    if issue := node.metadata.get("issue"):
        if not isinstance(issue, int):
            msg = f"Issue is not an integer: {issue}"
            raise TypeError(msg)

        return issue

    msg = f"Issue is not found in the node metadata: {node.metadata}"
    raise ValueError(msg)


class GithubIssueFromCommentNodePostprocessor(BaseNodePostprocessor):
    doc_store: BaseDocumentStore
    """The document store to get the parent nodes from."""

    @classmethod
    @override
    def class_name(cls) -> str:
        return "GithubIssueFromCommentNodePostprocessor"

    @override
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        # First we need to group the nodes by repository

        nodes_by_repository: dict[str, list[NodeWithScore]] = defaultdict(list)

        for node in nodes:
            if node_repository := get_repository_from_node(node=node.node):
                nodes_by_repository[node_repository].append(node)

        # For each repository, we need to group the nodes by issue number

        issue_documents_to_fetch: set[str] = set()

        for _, nodes_in_repository in nodes_by_repository.items():
            nodes_by_issue_number: dict[int, list[NodeWithScore]] = defaultdict(list)
            scores_by_issue_number: dict[int, list[float]] = defaultdict(list)

            for node_in_repository in nodes_in_repository:
                if issue := get_issue_from_node(node=node_in_repository.node):
                    nodes_by_issue_number[issue].append(node_in_repository)
                    if node_in_repository.score:
                        scores_by_issue_number[issue].append(node_in_repository.score)

            # For each issue number, we need to determine if we have already have the document for the issue

            for issue_number, nodes_in_issue in nodes_by_issue_number.items():
                if not any(get_type_from_node(node=node.node) == "issue" for node in nodes_in_issue):
                    issue_documents_to_fetch.add(issue_number)

            # Now we need to fetch the issue documents
            issue_documents: Sequence[BaseNode] = self.doc_store.get_nodes(node_ids=list(issue_documents_to_fetch))

            # Now we give these new documents scores based on the scores of the comment nodes

            for issue_document in issue_documents:
                if issue_number := get_issue_from_node(node=issue_document):  # noqa: SIM102
                    if issue_number in scores_by_issue_number:
                        node_with_score: NodeWithScore = NodeWithScore(node=issue_document, score=sum(scores_by_issue_number[issue_number]) / len(scores_by_issue_number[issue_number]))
                        nodes_in_repository.append(node_with_score)

        return nodes

    def _expand_nodes_with_parents(self, nodes_with_scores: list[NodeWithScore]) -> list[NodeWithScore]:
        """Expand nodes with parents."""

        gathered_parents: list[BaseNode] = []

        nodes_with_parents: list[NodeWithScore] = []

        parent_id_to_children: dict[str, list[NodeWithScore]] = defaultdict(list)

        for scored_node in nodes_with_scores:
            if scored_node.node.parent_node:
                parent_id_to_children[scored_node.node.parent_node.node_id].append(scored_node)
                nodes_with_parents.append(scored_node)

        processed_nodes: list[NodeWithScore] = nodes_with_parents.copy()

        for _ in range(self.rounds):
            self._expand_gathered_parents(nodes=processed_nodes, gathered_parents=gathered_parents)

            gathered_parents_by_id: dict[str, BaseNode] = {node.node_id: node for node in gathered_parents}

            processed_nodes = []

            for parent_id, children in parent_id_to_children.items():
                parent_node: BaseNode = gathered_parents_by_id[parent_id]

                # Make the type checker happy
                if not parent_node.child_nodes:
                    continue

                # If the children are not a significant enough portion of the parent, skip
                if len(children) / len(parent_node.child_nodes) < self.threshold:
                    processed_nodes.extend(children)
                    continue

                # If the parent node is too large, skip
                if len(parent_node.get_content(metadata_mode=MetadataMode.NONE)) > self.maximum_size:
                    processed_nodes.extend(children)
                    continue

                # Otherwise, merge the children into the parent
                processed_nodes.append(self._marge_children_scores_into_parent(parent_node=parent_node, children=children))

            nodes_with_parents = processed_nodes

        return nodes_with_parents

    def _expand_parentless_nodes(self, nodes_with_scores: list[NodeWithScore]) -> list[NodeWithScore]:
        """Expand parentless nodes."""

        gathered_next_nodes: list[BaseNode] = []

        parentless_nodes: list[NodeWithScore] = []

        for _ in range(self.rounds):
            self._expand_gathered_next_nodes(nodes=parentless_nodes, gathered_next_nodes=gathered_next_nodes)

            parentless_nodes = self._merge_adjacent_nodes(nodes_with_scores=nodes_with_scores, gathered_nodes=gathered_next_nodes)

        return parentless_nodes

    def _merge_adjacent_nodes(self, nodes_with_scores: list[NodeWithScore], gathered_nodes: list[BaseNode]) -> list[NodeWithScore]:
        """Merge adjacent nodes."""

        all_nodes: list[NodeWithScore] = nodes_with_scores.copy()
        gathered_nodes_by_id: dict[str, BaseNode] = {node.node_id: node for node in gathered_nodes}

        # Perform two rounds of merging to ensure we merge all adjacent nodes
        for _ in range(2):
            nodes_by_id: dict[str, NodeWithScore] = {node.node_id: node for node in all_nodes}

            removed_node_ids: set[str] = set()
            processed_nodes: list[NodeWithScore] = []

            for node_with_score in all_nodes:
                this_node: BaseNode = node_with_score.node

                # Make sure we haven't already merged this node
                if this_node.node_id in removed_node_ids:
                    continue

                # If this node has no next node, we'll return it as-is
                if not this_node.next_node:
                    processed_nodes.append(node_with_score)
                    continue

                second_node: NodeWithScore | BaseNode

                if nodes_by_id.get(this_node.next_node.node_id):
                    second_node = nodes_by_id[this_node.next_node.node_id]
                elif gathered_nodes_by_id.get(this_node.next_node.node_id):
                    second_node = gathered_nodes_by_id[this_node.next_node.node_id]
                else:
                    processed_nodes.append(node_with_score)
                    continue

                processed_nodes.append(self._new_node_from_siblings(scored_node=node_with_score, other_node=second_node))

            all_nodes = processed_nodes

        return all_nodes

    def _new_node_from_siblings(self, scored_node: NodeWithScore, other_node: NodeWithScore | BaseNode) -> NodeWithScore:
        """Create a new node from merged sibling nodes."""

        scored_nodes: list[NodeWithScore] = [scored_node]
        nodes: list[BaseNode] = [scored_node.node, other_node.node if isinstance(other_node, NodeWithScore) else other_node]

        if isinstance(other_node, BaseNode):
            scored_nodes.append(NodeWithScore(node=other_node, score=0))

        average_score = sum(node.score or 0 for node in scored_nodes) / len(scored_nodes)

        if len(scored_nodes) == 1:
            return scored_nodes[0]

        first_node: BaseNode = nodes[0]
        last_node: BaseNode = nodes[-1]

        new_node: Node = Node(
            text_resource=MediaResource(
                text="\n".join(node.get_content(metadata_mode=MetadataMode.NONE).strip() for node in nodes),
            ),
            extra_info=first_node.extra_info,
        )

        if first_node.prev_node:
            new_node.relationships[NodeRelationship.PREVIOUS] = first_node.prev_node

        if last_node.next_node:
            new_node.relationships[NodeRelationship.NEXT] = last_node.next_node

        return NodeWithScore(node=new_node, score=average_score)

    def _marge_children_scores_into_parent(self, parent_node: BaseNode, children: list[NodeWithScore]) -> NodeWithScore:
        """Create a new node with a score."""

        average_score = sum(node.score or 0 for node in children) / len(children)

        return NodeWithScore(node=parent_node, score=average_score)

    def _expand_gathered_parents(self, nodes: list[NodeWithScore], gathered_parents: list[BaseNode]) -> None:
        """Get the parent nodes of the nodes. Expanding the provided list of parent nodes."""

        parent_nodes_ids: list[str] = [node.node.parent_node.node_id for node in nodes if node.node.parent_node]

        gathered_parent_node_ids: list[str] = [node.node_id for node in gathered_parents]

        parent_nodes_to_gather: list[str] = [node_id for node_id in parent_nodes_ids if node_id not in gathered_parent_node_ids]

        new_parent_nodes: list[BaseNode] = self.doc_store.get_nodes(node_ids=parent_nodes_to_gather)

        gathered_parents.extend(new_parent_nodes)

    def _expand_gathered_next_nodes(self, nodes: list[NodeWithScore], gathered_next_nodes: list[BaseNode]) -> None:
        """Get the next nodes of the nodes."""

        next_nodes_ids: list[str] = [node.node.next_node.node_id for node in nodes if node.node.next_node]

        gathered_next_node_ids: list[str] = [node.node_id for node in gathered_next_nodes]

        next_nodes_to_gather: list[str] = [node_id for node_id in next_nodes_ids if node_id not in gathered_next_node_ids]

        new_next_nodes: list[BaseNode] = self.doc_store.get_nodes(node_ids=next_nodes_to_gather)

        gathered_next_nodes.extend(new_next_nodes)
