"""Uvicorn entry point for the local RAG API."""
import uvicorn

if __package__:
    from .app import app
else:
    from app import app


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
