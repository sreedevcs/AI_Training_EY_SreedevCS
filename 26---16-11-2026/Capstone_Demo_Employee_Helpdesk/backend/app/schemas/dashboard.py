
from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_tickets: int

    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_category: dict[str, int]
