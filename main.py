from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def index():
    return "hey"

@app.get("/blogs/{id}")
def getblogs(id: int):
    return {"id": id}

@app.get("/query")
def query(limit: int = 10, page: Optional[int] = 1):
    return {"limit": limit, "page": page}

class Body(BaseModel):
    title: str
    published_at: Optional[str]=None


@app.post("/body")
def body(body: Body):
    return {"body": body}

