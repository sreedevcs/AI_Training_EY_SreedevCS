
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from psycopg import Connection

from app.database import pool, get_db

from app.routers import tickets,assignments,dashboard,ai,ai_feedback

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open the PostgreSQL connection pool
    pool.open(wait=True)

    yield

    # Close the pool when the application shuts down
    pool.close()


app = FastAPI(
    title="AI-Powered Employee Helpdesk",
    description="Backend API for employee IT support management",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(tickets.router)
app.include_router(assignments.router,prefix="/api")
app.include_router(dashboard.router,prefix="/api")
app.include_router(ai.router,prefix="/api")
app.include_router(ai_feedback.router,prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Employee Helpdesk API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/db-check")
def database_check(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        result = cur.fetchone()

    return {
        "database": "connected",
        "postgresql_version": result[0]
    }
