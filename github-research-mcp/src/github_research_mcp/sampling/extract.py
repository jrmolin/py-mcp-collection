import json
from textwrap import dedent

from pydantic import BaseModel


def object_in_text_instructions[T: BaseModel](object_type: type[T], require: bool = False) -> str:
    """Return instructions for extracting an object from a text string."""

    instructions: str = dedent(
        text=f"""
A structured object of type {object_type.__name__} can be provided as a Markdown JSON block in your response."

The schema for the object is:
```json
{json.dumps(object_type.model_json_schema(), indent=2)}"
```

Example JSON block (a generic example, not valid for {object_type.__name__}):
```json
{{
    "property_1": "value_1"
    "property_2": "value_2"
    "property_3": "value_3"
}}
```

If you provide a JSON block, it must conform to the schema. When providing a JSON block, you may not provide any other
text other than the JSON block."""
    )

    if require:
        instructions += f"\n\nAny response other than providing the exact json block for {object_type.__name__} will be considered invalid."

    return instructions.strip()


def extract_json_blocks_from_text(text: str) -> list[str]:
    """Extract all JSON blocks from a text string."""

    lines = text.strip().split("\n")

    start_index: int | None = None
    end_index: int | None = None

    matches: list[str] = []

    for i, line in enumerate(lines):
        if line.startswith("```") and start_index is None:
            start_index = i + 1
            continue
        if line.startswith("```") and start_index is not None and end_index is None:
            end_index = i

        if start_index is not None and end_index is not None:
            matches.append("\n".join(lines[start_index:end_index]))
            start_index = None
            end_index = None

    return matches


def extract_single_object_from_json_block[T: BaseModel](json_block_text: str, object_type: type[T]) -> T | None:
    """Extract an object from a JSON block."""

    json_text: str = "\n".join([line.strip() for line in json_block_text.splitlines()])

    return object_type.model_validate_json(json_data=json_text)


def extract_single_object_from_text[T: BaseModel](text: str, object_type: type[T]) -> T | None:
    """Extract an object from a Markdown JSON block provided in the text string.

    For example:
    We should investigate the following users:
    ```json
    {
        "name": "John",
        "age": 30
    }

    And determine if they are valid reports of type errors.
    ```"""

    matches: list[str] = extract_json_blocks_from_text(text)

    if len(matches) != 1:
        msg = f"Text must contain exactly one Markdown JSON block. Received {text}."
        raise ValueError(msg)

    object_text: str = matches[0]

    return extract_single_object_from_json_block(json_block_text=object_text, object_type=object_type)
