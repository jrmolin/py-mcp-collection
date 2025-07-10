import random

from llama_index.core.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.core.schema import MediaResource, Node, NodeWithScore, QueryBundle

from knowledge_base_mcp.llama_index.post_processors.flash_rerank import FlashRankRerank


def test_init():
    reranker = FlashRankRerank()
    assert reranker is not None


def test_postprocess_nodes():
    reranker = FlashRankRerank()

    query_bundle = QueryBundle(query_str="I'm visiting New York City, what is the best place to get Bagels?")

    # Simulate bad results from a poor embedding model / query
    node_one = NodeWithScore(node=Node(text_resource=MediaResource(text="I'm just a Node i am only a Node"), id_="1"), score=0.9)
    node_two = NodeWithScore(
        node=Node(text_resource=MediaResource(text="The best place to get Bagels in New York City"), id_="2"), score=0.3
    )
    node_three = NodeWithScore(node=Node(text_resource=MediaResource(text="A Latte without milk is just an espresso"), id_="3"), score=1.0)

    nodes = [node_one, node_two, node_three]

    reranked_nodes = reranker.postprocess_nodes(nodes, query_bundle)

    assert reranked_nodes is not None
    assert len(reranked_nodes) == 3
    assert reranked_nodes[0] == node_two
    assert reranked_nodes[1] == node_three
    assert reranked_nodes[2] == node_one


class TestBenchmark:
    def generate_words(self, num_words: int) -> str:
        # read ./words.txt from https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain
        with open("tests/llama_index/post_processors/words.txt") as file:
            words = file.read().splitlines()

        # get random words
        # get random numbers from 0 to len(words)
        random_words = random.sample(words, num_words)
        return " ".join(random_words)

    def test_benchmark_flashrank_nodes(self, benchmark):
        def generate_nodes(num_nodes: int) -> list[NodeWithScore]:
            return [
                NodeWithScore(node=Node(text_resource=MediaResource(text=self.generate_words(100)), id_=f"{i}"), score=random.random())
                for i in range(num_nodes)
            ]

        reranker = FlashRankRerank(top_n=20)
        query_bundle = QueryBundle(query_str="I'm visiting New York City, what is the best place to get Bagels?")
        nodes = generate_nodes(num_nodes=200)

        result = benchmark(reranker.postprocess_nodes, nodes, query_bundle)
        assert result is not None
        assert len(result) == 20

    def test_benchmark_sentence_transformer_rerank(self, benchmark):
        def generate_nodes(num_nodes: int) -> list[NodeWithScore]:
            return [
                NodeWithScore(node=Node(text_resource=MediaResource(text=self.generate_words(100)), id_=f"{i}"), score=random.random())
                for i in range(num_nodes)
            ]

        reranker = SentenceTransformerRerank(top_n=20, device="cpu")
        query_bundle = QueryBundle(query_str="I'm visiting New York City, what is the best place to get Bagels?")
        nodes = generate_nodes(200)

        result = benchmark(reranker.postprocess_nodes, nodes, query_bundle)
        assert result is not None
        assert len(result) == 20
