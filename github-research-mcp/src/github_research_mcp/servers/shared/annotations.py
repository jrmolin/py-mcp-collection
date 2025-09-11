from enum import Enum
from typing import Annotated, Literal

from pydantic import Field

OWNER = Annotated[str, "The owner of the repository."]
REPO = Annotated[str, "The name of the repository."]
KEYWORDS = Annotated[set[str], "The keywords to search for in the issue. You may only provide up to 6 keywords."]
REQUIRE_ALL_KEYWORDS = Annotated[bool, "Whether all keywords must be present for a result to appear in the search results."]
STATE = Annotated[Literal["open", "closed", "all"], "The state of the issue."]

PAGE = Annotated[int, "The page of the search results."]
PER_PAGE = Annotated[int, "The number of results per page."]

LIMIT_COMMENTS = Annotated[int, Field(description="The maximum number of comments to include in the summary.")]
LIMIT_RELATED_ITEMS = Annotated[int, Field(description="The maximum number of related items to include in the summary.")]

# Summary Fields


class Length(int, Enum):
    SHORT = 500
    MEDIUM = 2000
    LONG = 4000


SUMMARY_LENGTH = Annotated["Length", Field(description="The length of the summary in words.")]
SUMMARY_FOCUS = Annotated[str, Field(description="The desired focus of the summary to be produced.")]
