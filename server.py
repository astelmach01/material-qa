from agents import SQLiteSession
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main import run_query

app = FastAPI()

DB_PATH = "conversation_history.db"

app.mount("/static", StaticFiles(directory="static"), name="static")


class Query(BaseModel):
    query: str
    user_id: str


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


@app.post("/query")
async def query_endpoint(query: Query):
    session = SQLiteSession(query.user_id, DB_PATH)
    response = await run_query(query.query, session)
    return response


@app.get("/articles/{user_id}")
async def get_articles_endpoint(user_id: str):
    session = SQLiteSession(session_id=user_id, db_path=DB_PATH)
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
    session = SQLiteSession(session_id=user_id, db_path=DB_PATH)
    items = await session.get_items()
    for item in items:
        if (
            item.get("role") == "tool_output"
            and item.get("content", {}).get("type") == "wikipedia_articles"
        ):
            return {"has_articles": True}
    return {"has_articles": False}
