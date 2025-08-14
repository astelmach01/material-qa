from fastapi import FastAPI
from pydantic import BaseModel

from main import run_query

app = FastAPI()

class Query(BaseModel):
    query: str

@app.post("/query")
async def query_endpoint(query: Query):
    answer = await run_query(query.query)
    return {"answer": answer}