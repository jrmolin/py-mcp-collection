from __future__ import annotations

from typing import TYPE_CHECKING, override

from marko.block import BlankLine
from marko.inline import RawText
from marko.parser import Parser, block, element, inline

if TYPE_CHECKING:
    from marko.source import Source

    BlockElementType = block.BlockElement
    InlineElementType = inline.InlineElement
    ElementType = element.Element


def pad_headings(headings: list[block.Heading | None], level: int) -> list[block.Heading | None]:
    for _ in range(len(headings), level + 1):
        _ = headings.append(None)
    return headings


def insert_heading(headings: list[block.Heading | None], new_heading: block.Heading) -> list[block.Heading | None]:
    headings = headings[: new_heading.level]

    headings = pad_headings(headings=headings, level=new_heading.level)

    headings[new_heading.level] = new_heading

    return headings


def get_highest_heading_level(headings: list[block.Heading | None]) -> int:
    for heading in headings:
        if heading:
            return heading.level
    return 0


def pop_heading(headings: list[block.Heading | None]) -> list[block.Heading | None]:
    headings_copy = headings.copy()
    _ = headings_copy.pop()
    # remove any trailing None values, leave non-trailing None values
    for i, heading in enumerate(reversed(headings_copy)):
        if heading is None:
            _ = headings_copy.pop()
        else:
            break

    return headings_copy


def get_parent_heading(headings: list[block.Heading | None]) -> block.Heading | None:
    # skip the last heading and get the second to last heading
    for heading in reversed(headings[:-1]):
        if heading is not None:
            return heading

    return None


def add_children(parent: block.BlockElement, child: block.BlockElement) -> block.BlockElement:
    current_children = parent.children
    parent.children = [*current_children, child]
    return parent


class GroupingParser(Parser):
    r"""
    All elements defined in CommonMark's spec are included in the parser
    by default.

    Attributes:
        block_elements(dict): a dict of name: block_element pairs
        inline_elements(dict): a dict of name: inline_element pairs

    :param \*extras: extra elements to be included in parsing process.
    """

    @override
    def parse_source(self, source: Source) -> list[block.BlockElement]:
        """Parse the source into a list of block elements."""
        element_list = self._build_block_element_list()

        headings: list[block.Heading | None] = []

        ast: list[block.BlockElement] = []
        while not source.exhausted:
            for ele_type in element_list:
                if ele_type.match(source):
                    result = ele_type.parse(source)  # pyright: ignore[reportAny]

                    if not hasattr(result, "priority"):  # pyright: ignore[reportAny]
                        # In some cases ``parse()`` won't return the element, but
                        # instead some information to create one, which will be passed
                        # to ``__init__()``.
                        result = ele_type(result)  # type: ignore  #  pyright: ignore[reportCallIssue]

                    if isinstance(result, block.Heading):
                        headings = insert_heading(headings=headings, new_heading=result)

                        parent_heading = get_parent_heading(headings=headings)
                        if parent_heading:
                            _ = add_children(parent=parent_heading, child=result)
                        else:
                            ast.append(result)

                        raw_text = result.inline_body
                        if raw_text:
                            # new_result = RawText(match=f"{"#" * result.level} {raw_text}")
                            new_result = RawText(match=raw_text)
                            blank_line = BlankLine(start=0)
                            result.inline_body = ""
                            result.children = [new_result, blank_line]

                    elif headings and headings[-1]:
                        current_children = headings[-1].children
                        headings[-1].children = [*current_children, result]
                    else:
                        ast.append(result)
                    break
            else:
                # Quit the current parsing and go back to the last level.
                break
        return ast
