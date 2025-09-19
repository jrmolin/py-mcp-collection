from textwrap import dedent
from typing import Self

import yaml
from mcp.types import SamplingMessage, TextContent
from pydantic import BaseModel, Field


class PromptSection(BaseModel):
    title: str = Field(description="The title of the section.")
    level: int = Field(default=1, description="The level of the section.")
    section: str = Field(description="The section of the prompt.")

    def render_text(self) -> str:
        return f"{'#' * self.level} {self.title}\n{self.section}"


WHO_YOU_ARE = PromptSection(
    title="Who you are",
    level=1,
    section="""
You are a helpful assistant that assists with researching GitHub repositories. You are an astute researcher that
is able to analyze GitHub repositories, issues, comments, pull requests, and other related items in order to help
a user with their GitHub-related tasks.
""",
)

DEEPLY_ROOTED = PromptSection(
    title="Deeply Rooted",
    level=1,
    section="""
Your work should always be entirely rooted in the provided information, not invented or made up. Every piece of information
you provide in your responses should be referencable back to a specific piece of information you were provided or that you
gathered. Whenever possible, you will indicate the source of the information in your responses.
""",
)

AVOID = PromptSection(
    title="Avoid Doing",
    level=1,
    section="""
You do not need to use hyperlinks for issues/pull requests that are in the same repository as the issue/pull request you are summarizing,
you can just provide the issue/pull request number. Just provide pull:# or issue:#. If the issue/pull request is not in the same repository,
you must provide the full URL to the issue/pull request.
""",
)

RESPONSE_FORMAT = PromptSection(
    title="Response Format",
    level=1,
    section="""
Your entire response will be provided directly to the user, so you should avoid extra language about how you will or
did do certain things. Begin your response with the summary, do not start with a header or with acknowledgement of the
task.

Your response should be in markdown format.
""",
)

SYSTEM_PROMPT_SECTIONS = [WHO_YOU_ARE, DEEPLY_ROOTED, RESPONSE_FORMAT, AVOID]

PREAMBLE = f"""
{WHO_YOU_ARE}

{DEEPLY_ROOTED}

{RESPONSE_FORMAT}

{AVOID}
"""


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
            yamled_objs = [yaml.safe_dump(obj, sort_keys=False) for obj in dumped_objs]
            yaml_text = "\n".join(yamled_objs)

        yaml_block: str = preamble or ""

        yaml_block += f"""
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

    def pop(self) -> PromptSection:
        return self.sections.pop()

    def reset(self) -> Self:
        self.sections = []
        return self

    def to_sampling_messages(self, one_message: bool = False) -> list[SamplingMessage]:
        if one_message:
            return [SamplingMessage(role="user", content=TextContent(type="text", text=self.render_text()))]

        return [SamplingMessage(role="user", content=TextContent(type="text", text=section.render_text())) for section in self.sections]


class SystemPromptBuilder(PromptBuilder):
    sections: list[PromptSection] = Field(default_factory=lambda: SYSTEM_PROMPT_SECTIONS.copy(), description="The sections of the prompt.")


class UserPromptBuilder(PromptBuilder):
    sections: list[PromptSection] = Field(default_factory=list, description="The sections of the prompt.")
