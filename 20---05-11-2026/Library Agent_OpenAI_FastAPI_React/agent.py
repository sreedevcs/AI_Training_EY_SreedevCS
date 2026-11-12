import json
import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from collections.abc import Callable    
from book_tools import reserve_book, search_books

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("Missing OPENAI_API_KEY. Add your OpenAI key to .env.")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": "Search the library catalog by book title or keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A book title or keyword to search for.",
                    },
                    "availability": {
                        "type": "string",
                        "enum": ["all", "available", "unavailable"],
                        "description": "Filter by copy availability.",
                    },
                },
                "required": ["query","availability"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reserve_book",
            "description": (
                "Reserve an available book for a customer. Use only when the user "
                "asks to reserve a book. The Python tool will ask for confirmation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "book_id": {
                        "type": "integer",
                        "description": "The ID of the book to reserve.",
                    },
                    "customer_name": {
                        "type": "string",
                        "description": "The name of the customer making the reservation.",
                    },
                },
                "required": ["book_id", "customer_name"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]

SYSTEM_PROMPT = """You are a helpful library assistant.

Use search_books to answer questions about the catalog and availability.
Use reserve_book only when the user asks to reserve a book.
If you need a book ID or customer name to make a reservation, ask the user.
The reservation tool asks for final confirmation. Do not say a reservation
was created unless the tool returns created=true. If the user asks for books with no available copies, call search_books
with availability="unavailable". If the search results show zero available copies, explain that those books
cannot be reserved right now. Do not call reserve_book for them.
Do not repeat the same search with the same arguments. If reserve_book returns confirmation_required, tell the user which book
and customer the reservation is for, then ask them to reply yes or no.
Do not say the reservation was created unless the tool returns created=true.
"""


def execute_tool(name: str, args: dict) -> dict:
    if name == "search_books":
        return search_books(
            query=args["query"],
            availability=args["availability"],
        )
    if name == "reserve_book":
        return reserve_book(
            book_id=args["book_id"],
            customer_name=args["customer_name"],
        )
    return {"error": f"Unknown tool: {name}"}


def answer_user(history: list[dict],tool_executor:Callable[[str, dict], dict]=execute_tool) -> str:
    """Let the model call tools, return their results, and produce a final answer."""
    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL,
            messages=history,
            tools=TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
            temperature=0,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            answer = message.content or "No answer generated."
            history.append({"role": "assistant", "content": answer})
            return answer

        history.append(message.model_dump(exclude_none=True))

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            print(f"\n[AGENT CHOSE TOOL] {name}")

            try:
                args = json.loads(tool_call.function.arguments)
                result = tool_executor(name, args)
            except (KeyError, TypeError, ValueError, OSError) as exc:
                result = {"error": str(exc)}

            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    return "Stopped after too many tool calls. Please try again."


def main() -> None:
    print("Library Book Agent")
    print("Model:", MODEL)
    print("Tools: search_books, reserve_book")
    print("Type 'exit' to quit.\n")

    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        question = input("You: ").strip()
        if question.casefold() in {"exit", "quit"}:
            break
        if not question:
            continue

        history.append({"role": "user", "content": question})

        try:
            answer = answer_user(history)
            print("\nAgent:", answer, "\n")
        except OpenAIError as exc:
            print("\nOpenAI API request failed:", exc, "\n")


if __name__ == "__main__":
    main()