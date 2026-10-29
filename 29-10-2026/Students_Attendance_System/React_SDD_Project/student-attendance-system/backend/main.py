from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from init_db import migrate_schema
from routers.students import router as students_router
from routers.attendance import router as attendance_router
from routers.reports import router as reports_router
from routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app):
    migrate_schema()
    yield


app = FastAPI(
    title="Student Attendance Management System API",
    description="Backend API for student attendance management",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(reports_router)
app.include_router(auth_router)
# Allow requests from the React development server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Student Attendance Management System API is running"
    }


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}

