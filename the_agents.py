from pathlib import Path
from typing import List

from agents import Agent
from pydantic import BaseModel, Field

from file_utils import hydrated_markdown_section_contents

ROOT_DIR = Path(__file__).parent
PROMPT_DIR = ROOT_DIR / "prompts"

HAIKU = "litellm/anthropic/claude-3-5-haiku-20241022"
SONNET = "litellm/anthropic/claude-sonnet-4-20250514"


class WikipediaQuery(BaseModel):
    explanation: str = Field(
        ...,
        description="Your internal thought process about what to query, not shown to "
        "anyone.",
    )
    wikipedia_articles: List[str] = Field(
        ...,
        description="A list of Wikipedia article titles to search for. "
        "These should be Wikipedia titles, e.g. 'Machine Learning', 'Elections in Japan'",
    )


query_agent = Agent(
    name="Query Agent",
    model=HAIKU,
    instructions=hydrated_markdown_section_contents(
        PROMPT_DIR / "query_agent.md", heading_name="System"
    ),
    output_type=WikipediaQuery,
)


class PrunedWikipediaArticle(BaseModel):
    explanation: str = Field(
        ..., description="Your internal thought processnot shown to anyone."
    )
    title: str = Field(
        ..., description="The original, unmodified title of the Wikipedia article."
    )
    last_edit: str = Field(
        ..., description="The timestamp of the last edit to the article."
    )
    cleaned_article_text: str = Field(
        ...,
        description="The cleaned text content of the original Wikipedia article, "
        "with only the relevant parts kept",
    )


article_pruner_agent = Agent(
    name="Article Pruner Agent",
    model=HAIKU,
    instructions=hydrated_markdown_section_contents(
        PROMPT_DIR / "article_pruner_agent.md", heading_name="System"
    ),
    output_type=PrunedWikipediaArticle,
)


class FinalUserResponse(BaseModel):
    thoughts: str = Field(
        ..., description="Your internal thought processnot shown to anyone."
    )
    answer: str = Field(..., description="The final answer to the user's question")


final_synthesizer_agent = Agent(
    name="Final Synthesizer Agent",
    model=SONNET,
    instructions=hydrated_markdown_section_contents(
        PROMPT_DIR / "final_synthesizer_agent.md", heading_name="System"
    ),
    output_type=FinalUserResponse,
)
