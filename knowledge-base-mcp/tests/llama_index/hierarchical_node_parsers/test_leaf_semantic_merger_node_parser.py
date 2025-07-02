from collections.abc import Sequence

import pytest
from llama_index.core.schema import BaseNode, Document, MediaResource, NodeRelationship, RelatedNodeInfo, TextNode
from llama_index.embeddings.fastembed import FastEmbedEmbedding

from knowledge_base_mcp.llama_index.hierarchical_node_parsers.hierarchical_node_parser import (
    GroupNode,
    RootNode,
    reset_prev_next_relationships,
)
from knowledge_base_mcp.llama_index.hierarchical_node_parsers.leaf_semantic_merging import LeafSemanticMergerNodeParser

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
def warsaw_nodes(embed_model: FastEmbedEmbedding, source_document_as_ref: RelatedNodeInfo) -> Sequence[BaseNode]:
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
    _ = embed_model(nodes=nodes)
    return nodes


@pytest.fixture
def football_nodes(embed_model: FastEmbedEmbedding, source_document_as_ref: RelatedNodeInfo) -> Sequence[BaseNode]:
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
    _ = embed_model(nodes=nodes)
    return nodes


@pytest.fixture
def mathematics_nodes(embed_model: FastEmbedEmbedding, source_document_as_ref: RelatedNodeInfo) -> list[TextNode]:
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
    _ = embed_model(nodes=nodes)
    return nodes


@pytest.fixture
def common_nodes(warsaw_nodes: list[TextNode], football_nodes: list[TextNode], mathematics_nodes: list[TextNode]) -> list[TextNode]:
    return [
        *warsaw_nodes,
        *football_nodes,
        *mathematics_nodes,
    ]


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_returns_all_nodes(embed_model: FastEmbedEmbedding, common_nodes: list[TextNode]) -> None:
    semantic_merger = LeafSemanticMergerNodeParser(
        embed_model=embed_model,
        max_token_count=256,
        merge_similarity_threshold=1.0,
        max_dissimilar_nodes=10,
    )

    nodes = await semantic_merger._aparse_nodes(nodes=common_nodes)  # pyright: ignore[reportPrivateUsage]
    assert len(nodes) == len(common_nodes)


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
async def test_warsaw_nodes(semantic_merger: LeafSemanticMergerNodeParser, warsaw_nodes: list[TextNode]) -> None:
    target_content = join_content(warsaw_nodes)

    merged_nodes = await semantic_merger._aparse_nodes(nodes=warsaw_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 1

    merged_node = merged_nodes[0]
    assert merged_node.get_content() == target_content, "Warsaw nodes were not correctly merged"

    assert merged_node.source_node is not None, "Source node was not set"
    assert merged_node.prev_node is None, "Previous node was not set"
    assert merged_node.next_node is None, "Next node was not set"

    # assert target_content == join_content(warsaw_nodes), "Original nodes were modified"
    # for node in warsaw_nodes:
    #     assert node.metadata == {"key": "value"}, "Original nodes were modified"


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_football_nodes(semantic_merger: LeafSemanticMergerNodeParser, football_nodes: list[TextNode]) -> None:
    target_content = join_content(football_nodes)

    merged_nodes = await semantic_merger._aparse_nodes(nodes=football_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 1
    assert merged_nodes[0].get_content() == target_content, "Football nodes were not correctly merged"

    # assert target_content == join_content(football_nodes), "Original nodes were modified"
    # for node in football_nodes:
    #     assert node.metadata == {"key": "value"}, "Original nodes were modified"


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_mathematics_nodes(semantic_merger: LeafSemanticMergerNodeParser, mathematics_nodes: list[TextNode]) -> None:
    target_content = join_content(mathematics_nodes)

    merged_nodes = await semantic_merger._aparse_nodes(nodes=mathematics_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 1
    assert merged_nodes[0].get_content() == target_content, "Mathematics nodes were not correctly merged"

    # assert target_content == join_content(mathematics_nodes), "Original nodes were modified"

    # for node in mathematics_nodes:
    #     assert node.metadata == {"key": "value"}, "Original nodes were modified"


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_combination_of_nodes(semantic_merger: LeafSemanticMergerNodeParser, common_nodes: list[TextNode]) -> None:  # pyright: ignore[reportPrivateUsage]
    warsaw_target_content = join_content(common_nodes[0:3])
    football_target_content = join_content(common_nodes[3:8])
    mathematics_target_content = join_content(common_nodes[8:10])

    merged_nodes = await semantic_merger._aparse_nodes(nodes=common_nodes)  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 3, "Number of returned nodes was not correct"

    assert merged_nodes[0].get_content() == warsaw_target_content, "Warsaw nodes were not correctly merged"

    assert merged_nodes[1].get_content() == football_target_content, "Football nodes were not correctly merged"

    assert merged_nodes[2].get_content() == mathematics_target_content, "Mathematics node was not correctly merged"

    # for node in common_nodes:
    #     assert node.metadata == {"key": "value"}, "Original nodes were modified"


@pytest.mark.skipif(not fastembed_available, reason="FastEmbed model not available")
async def test_groups_of_nodes(
    semantic_merger: LeafSemanticMergerNodeParser,
    warsaw_nodes: list[BaseNode],
    football_nodes: list[BaseNode],
    mathematics_nodes: list[BaseNode],
) -> None:  # pyright: ignore[reportPrivateUsage]
    warsaw_target_content = join_content(nodes=warsaw_nodes)
    football_target_content = join_content(nodes=football_nodes)
    mathematics_target_content = join_content(nodes=mathematics_nodes)

    warsaw_group = GroupNode(
        member_nodes=warsaw_nodes,
        text_resource=MediaResource(
            text=warsaw_target_content,
        ),
    )

    football_group = GroupNode(
        member_nodes=football_nodes,
        text_resource=MediaResource(
            text=football_target_content,
        ),
    )

    mathematics_group = GroupNode(
        member_nodes=mathematics_nodes,
        text_resource=MediaResource(
            text=mathematics_target_content,
        ),
    )

    root_node = RootNode(
        member_nodes=[warsaw_group, football_group, mathematics_group],
        text_resource=MediaResource(
            text=join_content(nodes=[*warsaw_nodes, *football_nodes, *mathematics_nodes]),
        ),
    )

    merged_nodes = await semantic_merger._aparse_nodes(nodes=root_node.descendant_nodes(leaf_nodes_only=True))  # pyright: ignore[reportPrivateUsage]

    assert len(merged_nodes) == 3, "Number of returned nodes was not correct"

    assert merged_nodes[0].get_content() == warsaw_target_content, "Warsaw nodes were not correctly merged"

    assert merged_nodes[1].get_content() == football_target_content, "Football nodes were not correctly merged"

    assert merged_nodes[2].get_content() == mathematics_target_content, "Mathematics node was not correctly merged"

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
