import asyncio

from agents import Runner
from the_agents import final_synthesizer_agent, FinalUserResponse, article_pruner_agent, PrunedWikipediaArticle, query_agent, WikipediaQuery, PROMPT_DIR
from tools.wikipedia import get_wikipedia_page
from file_utils import hydrated_markdown_section_contents

def format_pruned_articles(pruned_articles: list) -> list:
    """
    Formats the pruned articles into a list of strings.

    Args:
        pruned_articles: A list of pruned articles.

    Returns:
        A list of formatted strings.
    """
    return [
        f"Title: {article.title}\n"
        f"Last Edit: {article.last_edit}\n"
        f"Content: {article.cleaned_article_text}\n"
        for article in pruned_articles
    ]

async def run_final_synthesizer(query: str, formatted_articles: list):
    """
    Runs the final synthesizer agent.

    Args:
        query: The user's query.
        formatted_articles: A list of formatted pruned articles.

    Returns:
        The final answer to the user's query.
    """
    final_input = hydrated_markdown_section_contents(
        PROMPT_DIR / "final_synthesizer_agent.md",
        "Step 1",
        query=query,
        formatted_articles=formatted_articles
    )

    final_response = await Runner.run(
        final_synthesizer_agent,
        input=final_input
    )

    assert isinstance(final_response.final_output, FinalUserResponse)

    return final_response.final_output.answer

async def prune_articles(articles: list, query: str) -> list:
    """
    Prunes a list of Wikipedia articles using the article pruner agent.

    Args:
        articles: A list of Wikipedia articles to be pruned.
        query: The user's query.

    Returns:
        A list of pruned articles.
    """
    pruner_tasks = []
    seen_articles = set()
    for article in articles:
        if isinstance(article, str):
            print(f"Error fetching article: {article}")
            continue
        else:
            if article.title in seen_articles:
                print(f"Skipping duplicate article: {article.title}")
                continue
            
            seen_articles.add(article.title)
            pruner_input = hydrated_markdown_section_contents(
                PROMPT_DIR / "article_pruner_agent.md",
                "Step 1",
                article=article,
                question=query
            )
            pruner_tasks.append(Runner.run(article_pruner_agent, input=pruner_input))

    pruned_articles = await asyncio.gather(*pruner_tasks)
    pruned_articles = [res.final_output for res in pruned_articles]
    assert isinstance(pruned_articles, list)
    assert all(isinstance(a, PrunedWikipediaArticle) for a in pruned_articles)

    return pruned_articles

async def get_wikipedia_articles(query: str) -> list:
    """
    Gets a list of Wikipedia articles based on a query.

    Args:
        query: The user's query.

    Returns:
        A list of Wikipedia articles.
    """
    first_input = hydrated_markdown_section_contents(
        PROMPT_DIR / "query_agent.md", "Step 1", query=query)

    queries_articles = await Runner.run(query_agent,
                                        input=first_input)
    assert isinstance(queries_articles.final_output, WikipediaQuery)

    wikipedia_tasks = []
    for article_query in queries_articles.final_output.wikipedia_articles:
        wikipedia_tasks.append(get_wikipedia_page(article_query))

    return await asyncio.gather(*wikipedia_tasks)
