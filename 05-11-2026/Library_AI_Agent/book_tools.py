import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOOKS_PATH = ROOT / "books.json"
RESERVATIONS_PATH = ROOT / "reservations.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def search_books(query: str, availability: str = "all") -> dict:
    """Search by title/keyword and optionally filter by availability."""
    query = query.strip().casefold()
    availability = availability.casefold()

    if availability not in {"all", "available", "unavailable"}:
        return {
            "query": query,
            "matches": [],
            "message": "Invalid availability filter.",
        }

    # Also recognize availability requests expressed in natural language.
    unavailable_phrases = (
        "no available copies",
        "not available",
        "unavailable",
        "out of stock",
    )
    if any(phrase in query for phrase in unavailable_phrases):
        availability = "unavailable"
        query = ""

    books = read_json(BOOKS_PATH)
    terms = query.split()
    matches = []

    for book in books:
        copies = book["available_copies"]
        is_available = copies > 0

        if availability == "available" and not is_available:
            continue
        if availability == "unavailable" and is_available:
            continue

        searchable_text = " ".join(
            [book["title"], book["author"], *book.get("tags", [])]
        ).casefold()

        # An empty query with an availability filter means “show all books
        # matching that availability”; otherwise require a keyword match.
        if query and not (
            query in searchable_text
            or all(term in searchable_text for term in terms)
        ):
            continue

        matches.append({
            "id": book["id"],
            "title": book["title"],
            "author": book["author"],
            "available_copies": copies,
            "availability": "Available" if is_available else "Unavailable",
        })

    if availability == "unavailable":
        message = "Books with no available copies." if matches else "No unavailable books found."
    else:
        message = "Matching books found." if matches else "No matching books found."

    return {"query": query, "matches": matches, "message": message}

def reserve_book(book_id: int, customer_name: str) -> dict:
    """Reserve an available copy after asking for confirmation."""
    # book_id = book_id.strip()
    customer_name = customer_name.strip()

    if not book_id:
        return {"created": False, "reason": "Book ID is required."}
    if not customer_name:
        return {"created": False, "reason": "Customer name is required."}

    books = read_json(BOOKS_PATH)
    book = next(
        (item for item in books if item["id"] == book_id),
        None,
    )

    if book is None:
        return {"created": False, "reason": f"No book found with ID {book_id}."}

    if book["available_copies"] <= 0:
        return {
            "created": False,
            "reason": f"No copies of '{book['title']}' are currently available.",
        }

    print("\n--- RESERVATION CONFIRMATION ---")
    print(f"Book:     {book['title']} by {book['author']}")
    print(f"Book ID:  {book['id']}")
    print(f"Customer: {customer_name}")
    approval = input("Create this reservation? (y/n): ").strip().casefold()

    if approval not in {"y", "yes"}:
        return {"created": False, "reason": "Customer declined the reservation."}

    reservations = read_json(RESERVATIONS_PATH)
    next_number = max(
        [
            int(item["id"].split("-")[-1])
            for item in reservations
            if item.get("id", "").startswith("R-")
        ]
        or [0]
    ) + 1

    reservation = {
        "id": f"R-{next_number:04d}",
        "book_id": book["id"],
        "book_title": book["title"],
        "customer_name": customer_name,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    book["available_copies"] -= 1
    reservations.append(reservation)

    write_json(BOOKS_PATH, books)
    write_json(RESERVATIONS_PATH, reservations)

    return {"created": True, "reservation": reservation}

def create_reservation(book_id: int, customer_name: str) -> dict:
    customer_name = customer_name.strip()
    if not book_id:
        return {"created": False, "reason": "Book ID is required."}
    if not customer_name:
        return {"created": False, "reason": "Customer name is required."}
    
    books = read_json(BOOKS_PATH)
    book = next((item for item in books if item["id"] == book_id), None)

    if book is None:
        return {"created": False, "reason": f"No book found with ID {book_id}."}
    if book["available_copies"] <= 0:
        return {"created": False, "reason": f"No copies of '{book['title']}' are currently available."}

    reservations = read_json(RESERVATIONS_PATH)
    next_number = max(
        [
            int(item["id"].split("-")[-1])
            for item in reservations
            if item.get("id", "").startswith("R-")
        ]
        or [0]
    ) + 1

    reservation = {
        "id": f"R-{next_number:04d}",
        "book_id": book["id"],
        "book_title": book["title"],
        "customer_name": customer_name,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    book["available_copies"] -= 1
    reservations.append(reservation)
    write_json(BOOKS_PATH, books)
    write_json(RESERVATIONS_PATH, reservations)
    return {"created": True, "reservation": reservation}