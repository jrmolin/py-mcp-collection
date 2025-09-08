import json
from textwrap import dedent

from pydantic import BaseModel


def object_in_text_instructions[T: BaseModel](object_type: type[T], require: bool = False) -> str:
    """Return instructions for extracting an object from a text string."""

    instructions = f"""
        A structured object of type {object_type.__name__} can be provided as a Markdown JSON block in your response."

        The schema for the object is: {json.dumps(object_type.model_json_schema(), indent=2)}"

        Example JSON block (a generic example, not valid for {object_type.__name__}):
        ```json
        {{
            "property_1": "value_1"
            "property_2": "value_2"
            "property_3": "value_3"
        }}
        ```

        If you provide a JSON block, it must conform to the schema. When providing a JSON block, you may not provide any other
        text other than the JSON block.

        {f"Any response other than providing the exact json block for {object_type.__name__} will be considered invalid." if require else ""}
    """  # noqa: E501

    return dedent(text=instructions)


def extract_object_from_text[T: BaseModel](text: str, object_type: type[T]) -> T | None:
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

    lines = text.strip().split("\n")

    if not lines[0].startswith("```") and not lines[-1].startswith("```"):
        msg = "Text must be a Markdown JSON or YAML block"
        raise ValueError(msg)

    object_text = "\n".join(lines[1:-1])

    return object_type.model_validate_json(object_text)
