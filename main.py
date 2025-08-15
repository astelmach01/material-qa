import asyncio

from agents import Session

from src.utils import (
    format_pruned_articles,
    get_wikipedia_articles,
    prune_articles,
    run_final_synthesizer,
)


async def run_query(query: str, session: Session):
    print(f"Running query for session: {session.session_id}")
    wikipedia_articles = await get_wikipedia_articles(query, session)

    pruned_articles = await prune_articles(wikipedia_articles, query, session)

    formatted_articles = format_pruned_articles(pruned_articles)

    final_answer = await run_final_synthesizer(query, formatted_articles, session)

    return {"answer": final_answer, "articles": formatted_articles}


async def main():
    from agents import SQLiteSession

    query = "What are some uses of aluminium?"
    session = SQLiteSession("test_user", "conversation_history.db")
    response = await run_query(query, session)
    print(f"Final Answer: {response['answer']}")


if __name__ == "__main__":
    asyncio.run(main())
