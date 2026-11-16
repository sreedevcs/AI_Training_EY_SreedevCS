
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date

from app.database import (
    init_db,
    create_trip,
    get_trip_by_id,
    get_trips_by_employee
)

from app.memory import check_redis

from app.agent import ask_agent



app = FastAPI()


class TripCreate(BaseModel):
    employee_id: str
    destination: str
    start_date: date
    end_date: date
    purpose: str


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    question: str = Field(min_length=1)



@app.on_event("startup")
def startup():
    init_db()

    if not check_redis():
        raise RuntimeError("Redis connection failed")



@app.get("/")
def home():
    return {
        "message": "Travel and Weather Assistant is running"
    }



@app.post("/trips")
def register_trip(trip: TripCreate):

    if trip.end_date < trip.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    result = create_trip(
        employee_id=trip.employee_id,
        destination=trip.destination,
        start_date=str(trip.start_date),
        end_date=str(trip.end_date),
        purpose=trip.purpose
    )

    return {
        "message": "Trip registered successfully",
        "trip": result
    }



@app.get("/trips/{trip_id}")
def retrieve_trip(trip_id: int):

    trip = get_trip_by_id(trip_id)

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return trip



@app.get("/employees/{employee_id}/trips")
def retrieve_employee_trips(employee_id: str):

    trips = get_trips_by_employee(employee_id)

    return {
        "employee_id": employee_id,
        "total_trips": len(trips),
        "trips": trips
    }


@app.post("/chat")
def chat(request: ChatRequest):

    try:

        result = ask_agent(
            question=request.question,
            session_id=request.session_id
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Assistant execution failed: {str(e)}"
        )
