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
