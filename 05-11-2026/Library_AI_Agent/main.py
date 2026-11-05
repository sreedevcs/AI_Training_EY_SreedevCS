from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAIError
from pydantic import BaseModel, Field

import agent
from book_tools import (
    BOOKS_PATH,
    create_reservation,
    read_json,
    search_books,
)

app = FastAPI(title="Library Chat API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}
sessions_lock = Lock()


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=4000)


@app.post("/api/chat")
def chat(request: ChatRequest):
    with sessions_lock:
        session = sessions.setdefault(
            request.session_id,
            {
                "history": [{"role": "system", "content": agent.SYSTEM_PROMPT}],
                "pending_reservation": None,
                "lock": Lock(),
            },
        )

    with session["lock"]:
        pending = session["pending_reservation"]
        answer = request.message.strip().casefold()

        # Handle a confirmation in chat rather than waiting for terminal input.
        if pending:
            if answer in {"yes", "y"}:
                result = create_reservation(
                    pending["book_id"],
                    pending["customer_name"],
                )
                session["pending_reservation"] = None
                reply = (
                    f"Reservation created: {result['reservation']['book_title']}."
                    if result["created"]
                    else result["reason"]
                )
            elif answer in {"no", "n"}:
                session["pending_reservation"] = None
                reply = "Reservation cancelled."
            else:
                reply = "Please reply yes or no to confirm the reservation."

            session["history"].extend([
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": reply},
            ])
            return {"reply": reply}

        def web_tool_executor(name: str, args: dict) -> dict:
            if name == "search_books":
                return search_books(
                    query=args["query"],
                    availability=args["availability"],
                )

            if name == "reserve_book":
                book_id = args["book_id"]
                customer_name = args["customer_name"].strip()

                books = read_json(BOOKS_PATH)
                book = next(
                    (item for item in books if item["id"] == book_id),
                    None,
                )
                if book is None:
                    return {"created": False, "reason": "Book not found."}
                if book["available_copies"] <= 0:
                    return {
                        "created": False,
                        "reason": f"No copies of '{book['title']}' are available.",
                    }

                session["pending_reservation"] = {
                    "book_id": book_id,
                    "customer_name": customer_name,
                }
                return {
                    "confirmation_required": True,
                    "book": book["title"],
                    "customer_name": customer_name,
                }

            return {"error": f"Unknown tool: {name}"}

        session["history"].append({"role": "user", "content": request.message})

        try:
            reply = agent.answer_user(
                session["history"],
                tool_executor=web_tool_executor,
            )
        except OpenAIError as exc:
            raise HTTPException(status_code=502, detail="The model request failed.") from exc

        return {"reply": reply}