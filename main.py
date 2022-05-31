import time

from fastapi import FastAPI, Query
from typing import List
from app.routers import recipes

app = FastAPI(
    title="Recipe API"
)


@app.get("/")
def root() -> dict:
    """Root GET"""
    return {"message": "Рецепты!"}


app.include_router(recipes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )