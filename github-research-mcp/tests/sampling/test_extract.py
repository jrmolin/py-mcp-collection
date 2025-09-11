from textwrap import dedent

from inline_snapshot import snapshot
from pydantic import BaseModel

from github_research_mcp.sampling.extract import extract_json_blocks_from_text, extract_single_object_from_text, object_in_text_instructions


class TestObject(BaseModel):
    name: str
    age: int


def test_object_in_text_instructions():
    assert object_in_text_instructions(TestObject) == snapshot("""\
A structured object of type TestObject can be provided as a Markdown JSON block in your response."

The schema for the object is:
```json
{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "age": {
      "title": "Age",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "TestObject",
  "type": "object"
}"
```

Example JSON block (a generic example, not valid for TestObject):
```json
{
    "property_1": "value_1"
    "property_2": "value_2"
    "property_3": "value_3"
}
```

If you provide a JSON block, it must conform to the schema. When providing a JSON block, you may not provide any other
text other than the JSON block.\
""")


def test_extract_json_blocks_from_text():
    text = """
    This is a test text that occurs before the json block.
    ```json
    {
        "name": "John",
        "age": 30
    }
    ```

    ```json
    {
        "name": "Jane",
        "age": 25
    }
    ```

    This is a test text that occurs after the json block.
    """
    assert extract_json_blocks_from_text(text) == snapshot([])


def test_extract_single_object_from_text():
    text = dedent("""
    ```json
    {
        "name": "John",
        "age": 30
    }
    ```
    """)
    assert extract_single_object_from_text(text, TestObject) == TestObject(name="John", age=30)


def test_extract_object_from_text_extra_text():
    text = dedent("""
    Yes, I would be happy to provide the information you requested in a json block.
    ```json
    {
        "name": "John",
        "age": 30
    }
    ```

    This is a test text that occurs after the json block.
    """)
    assert extract_single_object_from_text(text, TestObject) == TestObject(name="John", age=30)
