import json
from pathlib import Path

from agent_framework import tool


DATA_FILE = Path(__file__).parent / "products.json"


def load_products():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


@tool(approval_mode="never_require")
def search_products(query: str) -> str:
    """Search products by name or category and return their details."""

    if not isinstance(query, str) or not query.strip():
        return json.dumps({"message": "Enter a product name or category to search."})

    search_term = query.strip().casefold()
    matches = [
        {
            "id": product["id"],
            "name": product["name"],
            "category": product["category"],
            "price_inr": product["price_inr"],
            "stock": product["stock"],
            "rating": product["rating"],
        }
        for product in load_products()
        if search_term in product["name"].casefold()
        or search_term in product["category"].casefold()
    ]

    if not matches:
        return json.dumps({"message": f"No products found matching '{query.strip()}'."})

    return json.dumps(matches)


@tool(approval_mode="never_require")
def calculate_order_total(product_id: str, quantity: int) -> str:
    """Calculate an order total after validating quantity and available stock."""

    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return json.dumps({"message": "Quantity must be a positive whole number."})
    if not isinstance(product_id, str) or not product_id.strip():
        return json.dumps({"message": "Enter a valid product ID."})

    product = next(
        (
            product
            for product in load_products()
            if product["id"].casefold() == product_id.strip().casefold()
        ),
        None,
    )
    if product is None:
        return json.dumps({"message": f"Product '{product_id}' was not found."})

    if quantity > product["stock"]:
        return json.dumps(
            {
                "message": (
                    f"Insufficient stock for product '{product_id}'. "
                    f"Requested {quantity}, available {product['stock']}."
                )
            }
        )

    return json.dumps(
        {
            "product_id": product["id"],
            "quantity": quantity,
            "unit_price_inr": product["price_inr"],
            "total_inr": product["price_inr"] * quantity,
        }
    )
