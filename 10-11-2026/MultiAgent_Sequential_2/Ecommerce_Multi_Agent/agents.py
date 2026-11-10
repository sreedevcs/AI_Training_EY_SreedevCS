import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient,OpenAIChatCompletionClient

from tools import calculate_order_total, search_products


def create_agents():
    """Create the inventory, pricing, and product recommendation agents."""

    # client = OpenAIChatClient(
    #     model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    # )
    client = OpenAIChatCompletionClient(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    )

    inventory_agent = Agent(
        client=client,
        name="InventoryAgent",
        instructions=(
            "You are a product inventory specialist. Understand the customer's "
            "requested product name or category, then use search_products to "
            "find matching products. Report each match's ID, name, category, "
            "price, rating, and stock availability. Clearly identify products "
            "with no stock. Pass all matching product details, along with the "
            "customer's requested quantity and budget, to the next agent. "
            "Never invent product details."
        ),
        tools=[search_products],
    )

    pricing_agent = Agent(
        client=client,
        name="PricingAgent",
        instructions=(
            "You are a product pricing specialist. Use the inventory results "
            "and the customer's requested quantity and budget. For every "
            "matching product, call calculate_order_total with its product ID "
            "and the requested quantity. Treat tool errors, including "
            "insufficient stock, as ineligible; never estimate or invent a "
            "total. Compare each verified total with the customer's budget "
            "and report which products are affordable. Pass the verified "
            "totals, stock/quantity eligibility, ratings, and budget status "
            "to the recommendation agent. If quantity or budget is missing, "
            "state that pricing cannot be completed without it."
        ),
        tools=[calculate_order_total],
    )

    recommendation_agent = Agent(
        client=client,
        name="RecommendationAgent",
        instructions=(
            "You are a product recommendation specialist. Review the "
            "inventory and pricing results and recommend the available "
            "product that satisfies the requested quantity and is within the "
            "customer's budget. Among eligible products, choose the highest "
            "rating; if ratings are equal, choose the lower verified total "
            "cost. Do not recommend out-of-stock products, products with "
            "insufficient stock, or products over budget. Give a short "
            "explanation using only verified product details and totals. If "
            "no product qualifies, say so clearly."
        ),
    )

    return inventory_agent, pricing_agent, recommendation_agent
