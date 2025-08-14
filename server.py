from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agents import SQLiteSession

from main import run_query

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


class Query(BaseModel):
    query: str
    user_id: str


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


@app.post("/query")
async def query_endpoint(query: Query):
    response = await run_query(query.query, query.user_id)
    return response


@app.get("/articles/{user_id}")
async def get_articles_endpoint(user_id: str):
    session = SQLiteSession(session_id=user_id)
    items = await session.get_items()
    articles = []
    for item in items:
        if (
            item.get("role") == "tool_output"
            and item.get("content", {}).get("type") == "wikipedia_articles"
        ):
            articles.extend(item["content"]["articles"])
    return {"articles": articles}


@app.get("/session_has_articles/{user_id}")
async def session_has_articles(user_id: str):
    """
    Checks if a session has articles.
    """
    session = SQLiteSession(session_id=user_id)
    items = await session.get_items()
    for item in items:
        if (
            item.get("role") == "tool_output"
            and item.get("content", {}).get("type") == "wikipedia_articles"
        ):
            return {"has_articles": True}
    return {"has_articles": False}
