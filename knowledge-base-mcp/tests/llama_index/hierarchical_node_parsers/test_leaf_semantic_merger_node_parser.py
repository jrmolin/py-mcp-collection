from collections.abc import Sequence

import pytest
from llama_index.core.schema import BaseNode, Document, NodeRelationship, RelatedNodeInfo, TextNode
from llama_index.embeddings.fastembed import FastEmbedEmbedding

from knowledge_base_mcp.llama_index.hierarchical_node_parsers.hierarchical_node_parser import (
    reset_prev_next_relationships,
)
from knowledge_base_mcp.llama_index.hierarchical_node_parsers.leaf_semantic_merging import LeafSemanticMergerNodeParser
from tests.llama_index.hierarchical_node_parsers.test_docling_hierarchical_node_parser import dedent

embedding_model: FastEmbedEmbedding | None = None
try:
    embedding_model = FastEmbedEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", embedding_cache=None)
    test = embedding_model._model.embed(["Hello, world!"])  # pyright: ignore[reportPrivateUsage]
    fastembed_available = True
except Exception:
    fastembed_available = False


def join_content(nodes: Sequence[BaseNode]) -> str:
    return ("\n\n".join([node.get_content() for node in nodes])).strip()


@pytest.fixture
def embed_model() -> FastEmbedEmbedding:
    if embedding_model is None:
        msg = "Embedding model not available"
        raise ValueError(msg)
    return embedding_model


@pytest.fixture
def source_document() -> Document:
    return Document()


@pytest.fixture
def source_document_as_ref(source_document: Document) -> RelatedNodeInfo:
    return source_document.as_related_node_info()


@pytest.fixture
def warsaw_nodes(embed_model: FastEmbedEmbedding, source_document_as_ref: RelatedNodeInfo) -> tuple[TextNode, list[TextNode]]:
    nodes = [
        TextNode(
            text="Warsaw: Warsaw, the capital city of Poland, is a bustling metropolis located on the banks of the Vistula River.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
        TextNode(
            text="It is known for its rich history, vibrant culture, and resilient spirit. Warsaw's skyline is characterized by a mix of historic architecture and modern skyscrapers.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
        TextNode(
            text="The Old Town, with its cobblestone streets and colorful buildings, is a UNESCO World Heritage Site.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
    ]

    reset_prev_next_relationships(sibling_nodes=nodes)

    parent_node = TextNode(
        text=dedent(
            """
            Warsaw: Warsaw, the capital city of Poland, is a bustling metropolis located on the banks of the Vistula River.

            It is known for its rich history, vibrant culture, and resilient spirit. Warsaw's skyline is characterized by a mix of historic architecture and modern skyscrapers.

            The Old Town, with its cobblestone streets and colorful buildings, is a UNESCO World Heritage Site.
            """
        ).strip(),
        relationships={
            NodeRelationship.SOURCE: source_document_as_ref,
            NodeRelationship.CHILD: [node.as_related_node_info() for node in nodes],
        },
    )

    for node in nodes:
        node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    _ = embed_model(nodes=nodes)

    return parent_node, nodes


@pytest.fixture
def football_nodes(embed_model: FastEmbedEmbedding, source_document_as_ref: RelatedNodeInfo) -> tuple[TextNode, list[TextNode]]:
    nodes = [
        TextNode(
            text="Football: Football, also known as soccer, is a popular sport played by millions of people worldwide.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
        TextNode(
            text="It is a team sport that involves two teams of eleven players each. The objective of the game is to score goals by kicking the ball into the opposing team's goal.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
        TextNode(
            text="Football matches are typically played on a rectangular field called a pitch, with goals at each end.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
        TextNode(
            text="The game is governed by a set of rules known as the Laws of the Game. Football is known for its passionate fanbase and intense rivalries between clubs and countries.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
        TextNode(
            text="The FIFA World Cup is the most prestigious international football tournament.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
    ]
    reset_prev_next_relationships(sibling_nodes=nodes)

    parent_node = TextNode(
        text=dedent(
            text="""
            Football: Football, also known as soccer, is a popular sport played by millions of people worldwide.

            It is a team sport that involves two teams of eleven players each. The objective of the game is to score goals by kicking the ball into the opposing team's goal.

            Football matches are typically played on a rectangular field called a pitch, with goals at each end.

            The game is governed by a set of rules known as the Laws of the Game. Football is known for its passionate fanbase and intense rivalries between clubs and countries.

            The FIFA World Cup is the most prestigious international football tournament.
            """
        ).strip(),
        relationships={
            NodeRelationship.SOURCE: source_document_as_ref,
            NodeRelationship.CHILD: [node.as_related_node_info() for node in nodes],
        },
    )

    _ = embed_model(nodes=nodes)

    for node in nodes:
        node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    return parent_node, nodes


@pytest.fixture
def mathematics_nodes(embed_model: FastEmbedEmbedding, source_document_as_ref: RelatedNodeInfo) -> tuple[TextNode, list[TextNode]]:
    nodes = [
        TextNode(
            text="Mathematics: Mathematics is a fundamental discipline that deals with the study of numbers, quantities, and shapes.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
        TextNode(
            text="Its branches include algebra, calculus, geometry, and statistics.",
            metadata={"key": "value"},
            relationships={NodeRelationship.SOURCE: source_document_as_ref},
        ),
    ]
    reset_prev_next_relationships(sibling_nodes=nodes)

    parent_node = TextNode(
        text=dedent(
            """
            Mathematics: Mathematics is a fundamental discipline that deals with the study of numbers, quantities, and shapes.

            Its branches include algebra, calculus, geometry, and statistics.
            """
        ).strip(),
        relationships={
            NodeRelationship.SOURCE: source_document_as_ref,
            NodeRelationship.CHILD: [node.as_related_node_info() for node in nodes],
        },
    )

    for node in nodes:
        node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    _ = embed_model(nodes=nodes)

    return parent_node, nodes


@pytest.fixture
def common_nodes(
    warsaw_nodes: tuple[TextNode, list[TextNode]],
    football_nodes: tuple[TextNode, list[TextNode]],
    mathematics_nodes: tuple[TextNode, list[TextNode]],
    source_document_as_ref: RelatedNodeInfo,
) -> tuple[TextNode, list[TextNode]]:
    _, warsaw_child_nodes = warsaw_nodes
    _, football_child_nodes = football_nodes
    _, mathematics_child_nodes = mathematics_nodes

    child_nodes = [
        *warsaw_child_nodes,
        *football_child_nodes,
        *mathematics_child_nodes,
    ]

    reset_prev_next_relationships(sibling_nodes=child_nodes)

    parent_node = TextNode(
        text=dedent(
            """
            Warsaw: Warsaw, the capital city of Poland, is a bustling metropolis located on the banks of the Vistula River.

            It is known for its rich history, vibrant culture, and resilient spirit. Warsaw's skyline is characterized by a mix of historic architecture and modern skyscrapers.

            The Old Town, with its cobblestone streets and colorful buildings, is a UNESCO World Heritage Site.

            Football: Football, also known as soccer, is a popular sport played by millions of people worldwide.

            It is a team sport that involves two teams of eleven players each. The objective of the game is to score goals by kicking the ball into the opposing team's goal.

            Football matches are typically played on a rectangular field called a pitch, with goals at each end.

            The game is governed by a set of rules known as the Laws of the Game. Football is known for its passionate fanbase and intense rivalries between clubs and countries.

            The FIFA World Cup is the most prestigious international football tournament.

            Mathematics: Mathematics is a fundamental discipline that deals with the study of numbers, quantities, and shapes.

            Its branches include algebra, calculus, geometry, and statistics.
            """
        ).strip(),
        relationships={
            NodeRelationship.SOURCE: source_document_as_ref,
            NodeRelationship.CHILD: [node.as_related_node_info() for node in child_nodes],
        },
    )

    for node in child_nodes:
        node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    reset_prev_next_relationships(sibling_nodes=child_nodes)

    return parent_node, child_nodes


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_returns_all_nodes(embed_model: FastEmbedEmbedding, common_nodes: tuple[TextNode, list[TextNode]]) -> None:
    parent_node, child_nodes = common_nodes

    all_nodes = [parent_node, *child_nodes]

    semantic_merger = LeafSemanticMergerNodeParser(
        embed_model=embed_model,
        max_token_count=256,
        merge_similarity_threshold=1.0,
        max_dissimilar_nodes=10,
    )

    nodes = await semantic_merger._aparse_nodes(nodes=all_nodes)  # pyright: ignore[reportPrivateUsage]
    assert len(nodes) == 11


# @pytest.fixture
# def recalculating_semantic_merger(embed_model: FastEmbedEmbedding) -> SemanticMergerNodeParser:
#     return SemanticMergerNodeParser(
#         embed_model=embed_model,
#         metadata_matching=["key"],
#         merge_similarity_threshold=0.5,
#         max_dissimilar_nodes=2,
#         embedding_strategy="recalculate",
#     )


@pytest.fixture
def semantic_merger(embed_model: FastEmbedEmbedding) -> LeafSemanticMergerNodeParser:
    return LeafSemanticMergerNodeParser(
        embed_model=embed_model,
        max_token_count=256,
        merge_similarity_threshold=0.5,
        max_dissimilar_nodes=2,
    )


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_warsaw_nodes(semantic_merger: LeafSemanticMergerNodeParser, warsaw_nodes: tuple[TextNode, list[TextNode]]) -> None:
    parent_node, child_nodes = warsaw_nodes

    all_nodes = [parent_node, *child_nodes]

    target_content = join_content(child_nodes)

    merged_nodes = await semantic_merger._aparse_nodes(nodes=all_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 2
    parent_node = merged_nodes[0]
    child_node = merged_nodes[1]

    assert parent_node.child_nodes == [child_node.as_related_node_info()]
    assert parent_node.prev_node is None
    assert parent_node.next_node is None

    assert child_node.parent_node == parent_node.as_related_node_info()
    assert child_node.prev_node is None
    assert child_node.next_node is None
    assert child_node.child_nodes is None

    assert parent_node.get_content() == target_content, "Warsaw nodes were not correctly merged"
    assert child_node.get_content() == target_content, "Child node was not correctly merged"


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_football_nodes(semantic_merger: LeafSemanticMergerNodeParser, football_nodes: tuple[TextNode, list[TextNode]]) -> None:
    parent_node, child_nodes = football_nodes

    all_nodes = [parent_node, *child_nodes]

    target_content = join_content(child_nodes)

    merged_nodes = await semantic_merger._aparse_nodes(nodes=all_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 2
    parent_node = merged_nodes[0]
    child_node = merged_nodes[1]

    assert parent_node.child_nodes == [child_node.as_related_node_info()]
    assert parent_node.prev_node is None
    assert parent_node.next_node is None
    assert child_node.parent_node == parent_node.as_related_node_info()

    assert parent_node.get_content() == target_content, "Parent node was not correctly merged"

    assert child_node.get_content() == target_content, "Child node was not correctly merged"

    # assert target_content == join_content(football_nodes), "Original nodes were modified"
    # for node in football_nodes:
    #     assert node.metadata == {"key": "value"}, "Original nodes were modified"


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_mathematics_nodes(semantic_merger: LeafSemanticMergerNodeParser, mathematics_nodes: tuple[TextNode, list[TextNode]]) -> None:
    parent_node, child_nodes = mathematics_nodes

    all_nodes = [parent_node, *child_nodes]

    target_content = join_content(child_nodes)

    merged_nodes = await semantic_merger._aparse_nodes(nodes=all_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 2
    parent_node = merged_nodes[0]
    child_node = merged_nodes[1]

    assert parent_node.child_nodes == [child_node.as_related_node_info()]
    assert parent_node.prev_node is None
    assert parent_node.next_node is None
    assert child_node.parent_node == parent_node.as_related_node_info()
    assert child_node.prev_node is None
    assert child_node.next_node is None
    assert child_node.child_nodes is None

    assert parent_node.get_content() == target_content, "Mathematics nodes were not correctly merged"
    assert child_node.get_content() == target_content, "Child node was not correctly merged"


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_combination_of_nodes(semantic_merger: LeafSemanticMergerNodeParser, common_nodes: tuple[TextNode, list[TextNode]]) -> None:  # pyright: ignore[reportPrivateUsage]
    parent_node, child_nodes = common_nodes

    all_nodes = [parent_node, *child_nodes]

    warsaw_target_content = join_content(child_nodes[0:3])
    football_target_content = join_content(child_nodes[3:8])
    mathematics_target_content = join_content(child_nodes[8:10])

    merged_nodes = await semantic_merger._aparse_nodes(nodes=all_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 4, "Number of returned nodes was not correct"

    assert merged_nodes[1].get_content() == warsaw_target_content, "Warsaw nodes were not correctly merged"

    assert merged_nodes[2].get_content() == football_target_content, "Football nodes were not correctly merged"

    assert merged_nodes[3].get_content() == mathematics_target_content, "Mathematics node was not correctly merged"


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_groups_of_nodes(
    source_document_as_ref: RelatedNodeInfo,
    semantic_merger: LeafSemanticMergerNodeParser,
    warsaw_nodes: tuple[TextNode, list[TextNode]],
    football_nodes: tuple[TextNode, list[TextNode]],
    mathematics_nodes: tuple[TextNode, list[TextNode]],
) -> None:
    warsaw_parent_node, warsaw_child_nodes = warsaw_nodes
    warsaw_target_content = join_content(warsaw_child_nodes)

    football_parent_node, football_child_nodes = football_nodes
    football_target_content = join_content(football_child_nodes)

    mathematics_parent_node, mathematics_child_nodes = mathematics_nodes
    mathematics_target_content = join_content(mathematics_child_nodes)

    parent_nodes = [warsaw_parent_node, football_parent_node, mathematics_parent_node]

    reset_prev_next_relationships(sibling_nodes=parent_nodes)
    child_nodes = [*warsaw_child_nodes, *football_child_nodes, *mathematics_child_nodes]

    root_node = TextNode(
        relationships={
            NodeRelationship.SOURCE: source_document_as_ref,
            NodeRelationship.CHILD: [node.as_related_node_info() for node in parent_nodes],
        },
    )

    for node in parent_nodes:
        node.relationships[NodeRelationship.PARENT] = root_node.as_related_node_info()

    all_nodes = [root_node, *parent_nodes, *child_nodes]
    merged_nodes = await semantic_merger._aparse_nodes(nodes=all_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 7, "Number of returned nodes was not correct"

    assert merged_nodes[2].get_content() == warsaw_target_content, "Warsaw nodes were not correctly merged"

    assert merged_nodes[4].get_content() == football_target_content, "Football nodes were not correctly merged"

    assert merged_nodes[6].get_content() == mathematics_target_content, "Mathematics node was not correctly merged"

    # for node in common_nodes:
    #     assert node.metadata == {"key": "value"}, "Original nodes were modified"


# @pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
# class TestPerformanceOfSemanticMerger:
#     async def test_performance_of_semantic_merger(
#         self,
#         semantic_merger: SemanticMergerNodeParser,
#         benchmark: BenchmarkFixture,
#         common_nodes: list[TextNode],
#     ) -> None:
#         merged_nodes = benchmark(semantic_merger.get_nodes_from_documents, documents=common_nodes)  # type: ignore

#         assert len(merged_nodes) == 3, "Number of returned nodes was not correct"

#         assert merged_nodes[0].get_content() == join_content(common_nodes[0:3]), "Warsaw nodes were not correctly merged"

#         assert merged_nodes[1].get_content() == join_content(common_nodes[3:8]), "Football nodes were not correctly merged"

#         assert merged_nodes[2].get_content() == join_content(common_nodes[8:10]), "Mathematics node was not correctly merged"

#     async def test_performance_of_semantic_merger_recalculate(
#         self,
#         recalculating_semantic_merger: SemanticMergerNodeParser,
#         benchmark: BenchmarkFixture,
#         common_nodes: list[TextNode],
#     ) -> None:
#         merged_nodes = benchmark(recalculating_semantic_merger.get_nodes_from_documents, documents=common_nodes)  # type: ignore

#         assert len(merged_nodes) == 3, "Number of returned nodes was not correct"

#         assert merged_nodes[0].get_content() == join_content(common_nodes[0:3]), "Warsaw nodes were not correctly merged"

#         assert merged_nodes[1].get_content() == join_content(common_nodes[3:8]), "Football nodes were not correctly merged"

#         assert merged_nodes[2].get_content() == join_content(common_nodes[8:10]), "Mathematics node was not correctly merged"


# @pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
# async def test_node_embedding_difference(
#     semantic_merger: SemanticMergerNodeParser,
#     recalculating_semantic_merger: SemanticMergerNodeParser,
#     embed_model: FastEmbedEmbedding,
#     common_nodes: list[TextNode],
# ) -> None:
#     merged_nodes = await semantic_merger.aget_nodes_from_documents(documents=common_nodes)  # type: ignore
#     recalculated_merged_nodes = await recalculating_semantic_merger.aget_nodes_from_documents(documents=common_nodes)  # type: ignore

#     assert len(merged_nodes) == 3, "Number of returned nodes was not correct"
#     assert len(recalculated_merged_nodes) == 3, "Number of returned nodes was not correct"

#     assert merged_nodes[0].get_content() == join_content(common_nodes[0:3]), "Warsaw nodes were not correctly merged"
#     assert recalculated_merged_nodes[0].get_content() == join_content(common_nodes[0:3]), "Warsaw nodes were not correctly merged"

#     assert merged_nodes[1].get_content() == join_content(common_nodes[3:8]), "Football nodes were not correctly merged"
#     assert recalculated_merged_nodes[1].get_content() == join_content(common_nodes[3:8]), "Football nodes were not correctly merged"

#     assert merged_nodes[2].get_content() == join_content(common_nodes[8:10]), "Mathematics node was not correctly merged"
#     assert recalculated_merged_nodes[2].get_content() == join_content(common_nodes[8:10]), "Mathematics node was not correctly merged"

#     for node, recalculated_node in zip(merged_nodes, recalculated_merged_nodes, strict=True):
#         assert node.embedding is not None, "Node embedding was not calculated"
#         assert recalculated_node.embedding is not None, "Recalculated node embedding was not calculated"

#         similarity = embed_model.similarity(node.embedding, recalculated_node.embedding)
#         assert similarity > 0.85, f"Node embeddings were not as close as expected: {similarity}"


# @pytest.fixture
# def euclidean_nodes(embed_model: FastEmbedEmbedding) -> list[TextNode]:
#     nodes = [
#         TextNode(
#             text="The following algorithm is framed as Knuth's 4-step version of Euclid's and Nicomachus', but rather than using division to find the remainder it uses successive subtractions of the shorter length s from the remaining length r until r is less than s. The high-level description, shown in boldface, is adapted from Knuth 1973:2-4:\n",
#             metadata={"key": "value"},
#         ),
#         TextNode(
#             text="INPUT:\n1 [Into two locations L and S put the numbers l and s that represent the two lengths]: INPUT L, S \n2 [Initialize R: make the remaining length r equal to the starting/initial/input length l]: R ? L \n",
#             metadata={"key": "value"},
#         ),
#         TextNode(
#             text="E0: [Ensure r ? s.]\n3 [Ensure the smaller of the two numbers is in S and the larger in R]: IF R > S THEN the contents of L is the larger number so skip over the exchange-steps ,and GOTO step ELSE swap the contents of R and S. 4 L ? R (this first step is redundant, but is useful for later discussion). 5 R ? S 6 S ? L",
#             metadata={"key": "value"},
#         ),
#         TextNode(
#             text="E1: [Find remainder]: Until the remaining length r in R is less than the shorter length s in S, repeatedly subtract the measuring number s in S from the remaining length r in R.\n7 IF S > R THEN done measuring so GOTO ELSE measure again, 8 R ? R ? S 9 [Remainder-loop]: GOTO . ",
#             metadata={"key": "value"},
#         ),
#         TextNode(
#             text="E2: [Is the remainder 0?]: EITHER (i) the last measure was exact and the remainder in R is 0 program can halt, OR (ii) the algorithm must continue: the last measure left a remainder in R less than measuring number in S.\n10 IF R = 0 THEN done so GOTO step 15 ELSE CONTINUE TO step 11,",
#             metadata={"key": "value"},
#         ),
#     ]
#     embed_model(nodes=nodes)
#     return nodes


# @pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
# async def test_euclidean_nodes(embed_model: FastEmbedEmbedding, euclidean_nodes: list[TextNode]) -> None:
#     semantic_merger = SemanticMergerNodeParser(
#         embed_model=embed_model,
#         metadata_matching=["key"],
#         merge_similarity_threshold=0.5,
#         max_dissimilar_nodes=3,
#         max_token_count=1500,
#     )
#     merged_nodes = await semantic_merger.aget_nodes_from_documents(documents=euclidean_nodes)  # type: ignore

#     assert len(merged_nodes) == 1, "Number of returned nodes was not correct"

#     assert merged_nodes[0].get_content() == join_content(euclidean_nodes), "Euclidean nodes were not correctly merged"

#     for node in euclidean_nodes:
#         assert node.metadata == {"key": "value"}, "Original nodes were modified"
