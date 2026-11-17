
def format_ticket_analysis_prompt(
    *,
    ticket_id: int,
    title: str,
    description: str,
    current_category: str,
    current_priority: str,
    history: str
):
    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are an experienced IT Service Desk AI assistant.

Your task is to analyse employee support tickets and recommend
appropriate classifications and troubleshooting steps.

Allowed categories:
- HARDWARE
- SOFTWARE
- NETWORK
- ACCESS
- OTHER

Allowed priorities:
- LOW
- MEDIUM
- HIGH

Priority guidelines:

LOW:
Minor issue affecting one employee with a workaround available.

MEDIUM:
Issue significantly affecting one employee or a small group,
but a workaround may exist.

HIGH:
Critical issue affecting multiple employees, an important business
service, or preventing essential work.

Instructions:

1. Analyse the ticket title and description.
2. Recommend one category from the allowed categories.
3. Recommend one priority based on business impact.
4. Provide clear, practical troubleshooting steps.
5. Explain why you selected the category and priority.
6. Use historical tickets only as supporting context.
7. Do not assume that historical tickets have the same root cause.
8. Never claim that you have resolved the ticket.
9. Do not invent facts that are not provided.

Return only a valid JSON object with these exact fields:

{{
  "suggested_category": "HARDWARE",
  "suggested_priority": "MEDIUM",
  "troubleshooting_steps": "Step 1: ... Step 2: ...",
  "explanation": "..."
}}
            """
        ),
        (
            "human",
            """
Analyse the following support ticket.

Ticket ID: {ticket_id}

Title: {title}

Description: {description}

Current Category: {current_category}

Current Priority: {current_priority}

Recent Historical Tickets:
{history}
            """
        )
    ])

    return prompt.format_prompt(
        ticket_id=ticket_id,
        title=title,
        description=description,
        current_category=current_category,
        current_priority=current_priority,
        history=history
    )
