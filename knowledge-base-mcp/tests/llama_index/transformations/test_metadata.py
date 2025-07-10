from llama_index.core.schema import MediaResource, MetadataMode, Node

from knowledge_base_mcp.llama_index.transformations.metadata import (
    AddMetadata,
    ExcludeMetadata,
    FlattenMetadata,
    IncludeMetadata,
    RemoveMetadata,
    RenameMetadata,
)


class TestAddMetadata:
    def test_init(self):
        add_metadata = AddMetadata(
            metadata={"key1": "value1", "key2": "value2"},
        )

        assert add_metadata.metadata == {"key1": "value1", "key2": "value2"}

    def test_call(self):
        node: Node = Node(
            text_resource=MediaResource(text="test"),
            extra_info={"key1": "value1", "key2": "value2"},
        )

        add_metadata = AddMetadata(
            metadata={"key3": "value3", "key4": "value4"},
        )

        nodes = add_metadata([node])

        this_node = nodes[0]

        assert this_node.metadata == {"key1": "value1", "key2": "value2", "key3": "value3", "key4": "value4"}


class TestIncludeMetadata:
    def test_init(self):
        include_metadata = IncludeMetadata(
            embed_keys=["key3", "key4"],
            llm_keys=["key5", "key6"],
        )

        assert include_metadata.embed_keys == ["key3", "key4"]
        assert include_metadata.llm_keys == ["key5", "key6"]

    def test_call(self):
        node: Node = Node(
            text_resource=MediaResource(text="test"),
            extra_info={"key1": "value1", "key2": "value2", "key3": "value3", "key4": "value4", "key5": "value5", "key6": "value6"},
        )

        include_metadata = IncludeMetadata(
            embed_keys=["key1", "key2"],
            llm_keys=["key3", "key4"],
        )

        nodes = include_metadata([node])

        this_node = nodes[0]

        assert this_node.excluded_embed_metadata_keys == ["key3", "key4", "key5", "key6"]
        assert this_node.excluded_llm_metadata_keys == ["key1", "key2", "key5", "key6"]

        embed_metadata_str = this_node.get_metadata_str(mode=MetadataMode.EMBED)
        assert embed_metadata_str == "key1: value1\nkey2: value2"

        llm_metadata_str = this_node.get_metadata_str(mode=MetadataMode.LLM)
        assert llm_metadata_str == "key3: value3\nkey4: value4"


class TestExcludeMetadata:
    def test_init(self):
        exclude_metadata = ExcludeMetadata(
            embed_keys=["key3", "key4"],
            llm_keys=["key5", "key6"],
        )

        assert exclude_metadata.embed_keys == ["key3", "key4"]
        assert exclude_metadata.llm_keys == ["key5", "key6"]

    def test_call(self):
        node: Node = Node(
            text_resource=MediaResource(text="test"),
            extra_info={"key1": "value1", "key2": "value2", "key3": "value3", "key4": "value4", "key5": "value5", "key6": "value6"},
        )

        exclude_metadata = ExcludeMetadata(
            embed_keys=["key1", "key2"],
            llm_keys=["key3", "key4"],
        )

        nodes = exclude_metadata([node])

        this_node = nodes[0]

        assert this_node.excluded_embed_metadata_keys == ["key1", "key2"]
        assert this_node.excluded_llm_metadata_keys == ["key3", "key4"]


class TestRenameMetadata:
    def test_init(self):
        rename_metadata = RenameMetadata(
            renames={"key1": "new_key1", "key2": "new_key2"},
        )

        assert rename_metadata.renames == {"key1": "new_key1", "key2": "new_key2"}

    def test_call(self):
        node: Node = Node(
            text_resource=MediaResource(text="test"),
            extra_info={"key1": "value1", "key2": "value2", "key3": "value3", "key4": "value4", "key5": "value5", "key6": "value6"},
        )

        rename_metadata = RenameMetadata(
            renames={"key1": "new_key1", "key2": "new_key2"},
        )

        nodes = rename_metadata([node])

        this_node = nodes[0]

        assert this_node.metadata == {
            "new_key1": "value1",
            "new_key2": "value2",
            "key3": "value3",
            "key4": "value4",
            "key5": "value5",
            "key6": "value6",
        }


class TestRemoveMetadata:
    def test_init(self):
        remove_metadata = RemoveMetadata(
            removals=["key1", "key2"],
        )

        assert remove_metadata.removals == ["key1", "key2"]

    def test_call(self):
        node: Node = Node(
            text_resource=MediaResource(text="test"),
            extra_info={"key1": "value1", "key2": "value2", "key3": "value3", "key4": "value4", "key5": "value5", "key6": "value6"},
        )

        remove_metadata = RemoveMetadata(
            removals=["key1", "key2"],
        )

        nodes = remove_metadata([node])

        this_node = nodes[0]

        assert this_node.metadata == {"key3": "value3", "key4": "value4", "key5": "value5", "key6": "value6"}


class TestFlattenMetadata:
    def test_init(self):
        flatten_metadata = FlattenMetadata()
        assert flatten_metadata

    def test_call(self):
        node: Node = Node(
            text_resource=MediaResource(text="test"),
            extra_info={"key1": {"key11": "value11", "key12": "value12"}, "key2": ["value21", "value22"]},
        )

        flatten_metadata = FlattenMetadata()

        nodes = flatten_metadata([node])

        this_node = nodes[0]

        assert this_node.metadata.get("key1") == '{"key11": "value11", "key12": "value12"}'
        assert this_node.metadata.get("key2") == "value21, value22"
