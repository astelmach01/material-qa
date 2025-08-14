import asyncio

from utils import get_wikipedia_articles, prune_articles, format_pruned_articles, run_final_synthesizer



async def run_query(query: str):
    wikipedia_articles = await get_wikipedia_articles(query)

    pruned_articles = await prune_articles(wikipedia_articles, query)

    formatted_articles = format_pruned_articles(pruned_articles)

    final_answer = await run_final_synthesizer(query, formatted_articles)

    return final_answer


async def main():
    query = "What are some uses of aluminium?"
    answer = await run_query(query)
    print(f"Final Answer: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
