
import json
from pathlib import Path
from langchain.tools import tool

FILE = Path(__file__).parent / "workshops.json"
COUPONS_FILE = Path(__file__).parent / "coupons.json"


def get_workshops():
    return json.loads(FILE.read_text(encoding="utf-8"))


@tool
def search_workshops(keyword: str) -> str:
    """Search available workshops by title."""

    matches = [
        w for w in get_workshops()
        if keyword.lower() in w["title"].lower()
    ]

    return json.dumps(matches)


@tool
def calculate_workshop_fee(
    workshop_id: str,
    participants: int
) -> str:
    """Calculate the total fee for a workshop and participant count."""
    if participants < 1 or participants > 30:
        return "Participant count must be between 1 and 30."
    for workshop in get_workshops():

        if workshop["id"] == workshop_id:
            total = workshop["fee"] * participants

            return json.dumps({
                "workshop": workshop["title"],
                "participants": participants,
                "total_fee": total
            })

    return "Workshop not found."


@tool
def list_all_workshops() -> str:
    """List all available workshops."""
    workshops = get_workshops()
    return json.dumps(workshops)


@tool
def find_cheapest_workshop() -> str:
    """Find the workshop with the lowest fee."""
    workshops = get_workshops()
    if not workshops:
        return "No workshops available."

    cheapest = min(workshops, key=lambda w: w["fee"])
    return json.dumps(cheapest)


def get_coupons():
    return json.loads(COUPONS_FILE.read_text(encoding="utf-8"))


@tool
def apply_coupon_code(original_fee: float, coupon_code: str) -> str:
    """Apply a coupon code to the original fee and return the discounted fee."""
    coupons = get_coupons()
    code = coupon_code.upper()  # make it case insensitive

    if code in coupons:
        discount_rate = coupons[code]
        discount_amount = original_fee * discount_rate
        final_fee = original_fee - discount_amount
        return json.dumps({
            "original_fee": original_fee,
            "coupon_code": code,
            "discount_rate": discount_rate,
            "discount_amount": discount_amount,
            "final_fee": final_fee
        })
    else:
        return json.dumps({
            "original_fee": original_fee,
            "coupon_code": code,
            "error": "Invalid coupon code."
        })

if __name__ == "__main__":
    print(search_workshops.invoke({"keyword": "Python"}))

    print(calculate_workshop_fee.invoke({
        "workshop_id": "W101",
        "participants": 4
    }))
