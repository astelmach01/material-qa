import asyncio

from agents import Runner

from the_agents import query_agent, WikipediaQuery, PROMPT_DIR, PrunedWikipediaArticle, \
    article_pruner_agent, final_synthesizer_agent, FinalUserResponse
from tools.wikipedia import get_wikipedia_page
from utils import hydrated_markdown_section_contents


async def main():
    query = "What are some uses of aluminium?"
    first_input = hydrated_markdown_section_contents(
        PROMPT_DIR / "query_agent.md", "Step 1", query=query)

    queries_articles = await Runner.run(query_agent,
                                        input=first_input)
    assert isinstance(queries_articles.final_output, WikipediaQuery)

    wikipedia_tasks = []
    for article_query in queries_articles.final_output.wikipedia_articles:
        wikipedia_tasks.append(get_wikipedia_page(article_query))

    wikipedia_articles = await asyncio.gather(*wikipedia_tasks)

    pruner_tasks = []
    seen_articles = set()
    for article in wikipedia_articles:
        if isinstance(article, str):
            print(f"Error fetching article: {article}")
            continue
        else:
            if str(article) in seen_articles:
                print(f"Skipping duplicate article: {article.title}")
                continue

            seen_articles.add(str(article))
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

    formatted_articles = [
        f"Title: {article.title}\n"
        f"Last Edit: {article.last_edit}\n"
        f"Content: {article.cleaned_article_text}\n"
        for article in pruned_articles
    ]

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

    print(f"Final Answer: {final_response.final_output.answer}")



if __name__ == "__main__":
    asyncio.run(main())
