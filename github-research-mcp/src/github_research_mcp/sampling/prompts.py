from collections.abc import Sequence
from textwrap import dedent
from typing import Self

import yaml
from mcp.types import SamplingMessage, TextContent
from pydantic import BaseModel, Field

WHO_YOU_ARE = """
# Who you are
You are a helpful assistant that summarizes issues on GitHub. You are an astute researcher that is able to analyze GitHub issues, comments,
pull requests, and other related items.
"""

DEEPLY_ROOTED = """
Your summary should be entirely rooted in the provided information, not invented or made up. Every item in the
summary should include a link/reference to the comment, issue, or related item that the information is based on
to ensure that the user can gather additional information if they are interested.
"""

AVOID = """
You do not need to use hyperlinks for issues/pull requests that are in the same repository as the issue/pull request you are summarizing,
you can just provide the issue/pull request number. Just provide pull:# or issue:#. If the issue/pull request is not in the same repository,
you must provide the full URL to the issue/pull request.
"""

RESPONSE_FORMAT = """
Your entire response will be provided directly to the user, so you should avoid extra language about how you will or
did do certain things. Begin your response with the summary, do not start with a header or with acknowledgement of the
task.

Your response should be in markdown format.
"""


PREAMBLE = f"""
{WHO_YOU_ARE}

{DEEPLY_ROOTED}

{RESPONSE_FORMAT}

{AVOID}
"""


class PromptSection(BaseModel):
    title: str = Field(description="The title of the section.")
    level: int = Field(default=1, description="The level of the section.")
    section: str = Field(description="The section of the prompt.")

    def render_text(self) -> str:
        return f"{'#' * self.level} {self.title}\n{self.section}"


class PromptBuilder(BaseModel):
    sections: list[PromptSection] = Field(default_factory=list, description="The sections of the prompt.")

    def add_text_section(self, title: str, text: str | list[str], level: int = 1) -> Self:
        if not isinstance(text, list):
            text = [text]

        text_block = "\n".join([dedent(text) for text in text])

        self.sections.append(PromptSection(title=title, level=level, section=text_block))

        return self

    def add_code_section(self, title: str, code: str, language: str, level: int = 1) -> Self:
        code_block = dedent(f"""
        ```{language}
        {code}
        ```
        """)

        self.sections.append(PromptSection(title=title, level=level, section=code_block))

        return self

    def add_yaml_section(self, title: str, obj: str | dict | BaseModel | list, preamble: str | None = None, level: int = 1) -> Self:
        yaml_text: str

        if isinstance(obj, str):
            yaml_text = obj
        elif isinstance(obj, BaseModel):
            yaml_text = yaml.safe_dump(obj.model_dump(), sort_keys=False)
        elif isinstance(obj, dict):
            yaml_text = yaml.safe_dump(obj, sort_keys=False)
        elif isinstance(obj, list):
            dumped_objs = [obj.model_dump() if isinstance(obj, BaseModel) else obj for obj in obj]
            yaml_text = yaml.safe_dump_all(dumped_objs, sort_keys=False)

        yaml_block = f"""{preamble}
```yaml
{yaml_text}
```"""

        self.sections.append(PromptSection(title=title, level=level, section=yaml_block))

        return self

    def add_prompt_section(self, section: PromptSection) -> Self:
        self.sections.append(section)
        return self

    def render_text(self) -> str:
        return "\n\n".join(section.render_text() for section in self.sections)

    def to_sampling_messages(self) -> Sequence[SamplingMessage]:
        return [SamplingMessage(role="user", content=TextContent(type="text", text=self.render_text()))]


class SystemPromptBuilder(PromptBuilder):
    sections: list[PromptSection] = Field(
        default_factory=lambda: [PromptSection(title="System Prompt", level=1, section=PREAMBLE)], description="The sections of the prompt."
    )
