from datetime import datetime
from pathlib import Path

from fastmcp.contrib.mcp_mixin import MCPMixin, mcp_tool
from pydantic import BaseModel, Field


class ReferenceEntry(BaseModel):
    name: str = Field(description="The name of the reference entry")
    path: Path = Field(description="The path to the reference entry file")

    def get_length(self) -> int:
        with self.path.open("r") as f:
            return len(f.read())

    def get_content(self, head: int | None = None) -> str:
        with self.path.open("r") as f:
            return f.read()[:head]

    def get_preview(self, preview_size: int) -> str:
        content = self.get_content(preview_size)

        # Get everything before the first double newline
        content = content.split("\n\n")[0] if "\n\n" in content else content

        # Truncate to the preview size
        content = content[:preview_size]

        # If the content is longer than the preview size, add an ellipsis
        if self.get_length() > preview_size:
            content = "Preview: " + content + "..."

        return content

    def render(self, reference_type: str, preview: bool, preview_size: int) -> str:
        contents = [
            f"### Type: `{reference_type}`, Name: `{self.name}`\n",
            self.get_content() if not preview else self.get_preview(preview_size),
            "\n",
        ]
        return "".join(contents)


class Reference(BaseModel):
    type: str = Field(description="The type of reference")
    path: Path = Field(description="The path to the reference file")

    @property
    def description(self) -> str:
        readme = self.path / "README.md"
        if readme.exists():
            return readme.read_text()
        return ""

    @classmethod
    def from_reference_string(cls, reference_string: str) -> "Reference":
        if ":" in reference_string:
            reference_type, path = reference_string.split(":")
            reference_path = Path(path)
        else:
            reference_path = Path(reference_string)
            reference_type = reference_path.stem

        return cls(type=reference_type, path=reference_path)

    def get_entries(self) -> list[ReferenceEntry]:
        # Get the markdown files in the directory
        return [ReferenceEntry(name=file.stem, path=file) for file in self.path.glob("*.md") if file.stem != "README"]

    def get_entry_by_name(self, name: str) -> ReferenceEntry:
        entries = self.get_entries()
        for entry in entries:
            if entry.name == name:
                return entry
        msg = f"No entry found with name {name}"
        raise ValueError(msg)

    def has_entry(self, name: str) -> bool:
        try:
            self.get_entry_by_name(name)
        except ValueError:
            return False

        return True

    def render(self, preview: bool, preview_size: int) -> str:
        contents = [
            f"## References for: `{self.type}`\n",
            self.description,
            "\n\n",
            "\n".join([entry.render(self.type, preview, preview_size) for entry in self.get_entries()]),
            "\n",
        ]
        return "".join(contents)


class ReferenceManager(MCPMixin):
    references: list[Reference]
    last_refreshed: datetime
    preview_size: int

    def __init__(self, references: list[Reference], preview_size: int):
        self.preview_size = preview_size
        self.references = references

    @classmethod
    def from_reference_strings(cls, reference_strings: list[str], preview_size: int) -> "ReferenceManager":
        return cls([Reference.from_reference_string(reference) for reference in reference_strings], preview_size)

    @mcp_tool()
    def preview_references(self) -> str:
        """Preview all references

        Returns:
            Formatted text describing the types of references and their available entries

        Example:
        >>> preview_references()
        # Local References

        ## Reference Type: Best Practices
        This is a description of the README reference type.

        ### Thing 1
        This is a preview of the best practice for thing 1.

        ### Thing 2
        This is a preview of the best practice for thing 2.
        """
        content = [
            "# Local References\n",
            "Below is a list of available reference types. We will show each type, and a preview of its entries.",
            f"Note: previews are truncated to {self.preview_size} characters.\n\n",
            "\n".join(
                [
                    reference.render(
                        preview=True,
                        preview_size=self.preview_size,
                    )
                    for reference in self.references
                ]
            ),
            "\n",
        ]
        return ("".join(content)).rstrip()

    @mcp_tool()
    def get_reference(self, reference_type: str, reference_name: str) -> str:
        """Get a reference by type and name

        Args:
            reference_type: The type of reference to get
            reference_name: The name of the reference to get

        Returns:
            The content of the reference

        Example:
        >>> get_reference("Best Practices", "Thing 1")
        This is a best practice for thing 1. It goes on much longer than the preview
        """
        for reference in self.references:
            if reference.type == reference_type:
                return reference.get_entry_by_name(reference_name).get_content()

        msg = f"No reference found with type {reference_type} and name {reference_name}"
        raise ValueError(msg)
