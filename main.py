import asyncio

from utils import (
    format_pruned_articles,
    get_wikipedia_articles,
    prune_articles,
    run_final_synthesizer,
)


async def run_query(query: str, user_id: str):
    wikipedia_articles = await get_wikipedia_articles(query)

    pruned_articles = await prune_articles(wikipedia_articles, query)

    formatted_articles = format_pruned_articles(pruned_articles)

    final_answer = await run_final_synthesizer(query, formatted_articles, user_id)

    return {"answer": final_answer, "articles": formatted_articles}


async def main():
    query = "What are some uses of aluminium?"
    response = await run_query(query, "test_user")
    print(f"Final Answer: {response['answer']}")


if __name__ == "__main__":
    asyncio.run(main())
