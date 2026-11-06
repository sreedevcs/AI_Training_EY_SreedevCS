import json
import re
from pathlib import Path

from langchain.tools import tool

from guardrails import validate_guest_count

DATA_FILE = Path(__file__).resolve().parent / "restaurants.json"

def load_restaurants()->list[dict]:
    with DATA_FILE.open(encoding="utf-8") as f:
        return json.load(f)

@tool
def search_restaurants(keyword:str)->str:
    """Search restaurants by cuisine, name, or location and return prices and available seats."""
    catalog=load_restaurants()
    query=keyword.strip().lower()
    if not query or query in {"all","list","available","restaurants"}:
        matches=catalog
    else:
        words=[it for it in re.findall(r"[a-z0-9]+",query) if len(it)>2]
        matches=[restaurant for restaurant in catalog if any (word in (restaurant["name"]+" "+restaurant["cuisine"]+" "+restaurant["location"]).lower() for word in words)]
    if not matches:
        return "No matching restaurants found. Ask to list all the restaurants"
    return json.dumps(matches,ensure_ascii=False,indent=2)

@tool
def calculate_dining_cost(restaurant_id:str,guests:int)->str:
    """Estimate the total dining cost and warn if there are not enough available seats."""
    valid,message=validate_guest_count(guests)
    if not valid:
        return message
    restaurant=next((it for it in load_restaurants() if it["id"].upper() == restaurant_id.strip().upper()),None,)
    if restaurant is None:
        return "Unknown restaurant ID. Use search_restaurants to find the correct ID."
    total=restaurant["price_per_person"]*guests
    result = {
        "id": restaurant["id"],
        "name": restaurant["name"],
        "cuisine": restaurant["cuisine"],
        "price_per_person": restaurant["price_per_person"],
        "available_seats": restaurant["available_seats"],
        "guests": guests,
        "total_price": total,
    }

    if guests > restaurant["available_seats"]:
        result["seating_warning"] = (
            f"Only {restaurant['available_seats']} seats are available, "
            f"but the guest count is {guests}."
        )

    return json.dumps(result, ensure_ascii=False, indent=2)