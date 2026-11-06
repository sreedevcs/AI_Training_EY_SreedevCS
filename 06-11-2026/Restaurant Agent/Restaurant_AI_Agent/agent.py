import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from tools import search_restaurants,calculate_dining_cost
from guardrails import check_input,clean_output
load_dotenv(Path(__file__).resolve().parent / ".env")
if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("Missing OPENAI_API_KEY. Create .env using .env.example.")

model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
model = ChatOpenAI(model=model_name, temperature=0)

agent = create_agent(
    model=model,
    tools=[search_restaurants,calculate_dining_cost],
    system_prompt=(
        "You are a friendly workshop enquiry assistant. "
        "Help users explore restaurants and calculate estimated dining costs. "
        "Use search_restaurants for restaurant information. "
        "Use calculate_dining_cost for all dining cost calculations. "
        "Never invent restaurant names, cuisines, prices or seating availability. "
        "Use only information returned by the tools. "
        "Remember previously selected restaurants and guest counts from earlier messages in the same conversation. "
        "If the user says 'make that 6 people', use the previously selected restaurant to recalculate the cost. "
        "Guest count must be between 1 and 20. "
        "You cannot make actual restaurant reservations or process payments."
        "Keep responses concise."
    ),
    checkpointer=InMemorySaver(),
)
thread_number=1
thread_id=f"restaurant-agent-{thread_number}"
message_count=0
has_context=False

print(f"Restaurant Agent | Model: {model_name}")
print("Commands: /new to begin another conversation, exit to quit")
print("Try: 'Show me Indian restaurants.'")

while True:
    question=input("\nYou: ").strip()
    if question.lower()=="exit":
        break

    if question.lower()=="/new":
        thread_number=thread_number+1
        thread_id=f"restaurant-agent-{thread_number}"
        message_count=0
        has_context=False
        print("Started new conversation. Previous thread details are not shared.")
        continue
    if not question:
        continue
    valid,message=check_input(question,has_context)
    if not valid:
        print("\nAgent:",message)
        continue
    config={
        "configurable":{"thread_id":thread_id}
    }

    try:
        result=agent.invoke({"messages":[{"role":"user","content":question}]},config=config,)
    except Exception as e:
        print(f"Agent request failed: {e}")
        continue

    messages=result["messages"]
    new_messages=messages[message_count:]
    message_count=len(messages)

    for message in new_messages:
        if isinstance(message,AIMessage):
            for call in message.tool_calls:
                print(f"[AGENT CHOSE TOOL]{call['name']}"
                      f"| Arguments: {call['args']}")
        elif isinstance(message,ToolMessage):
            print(f"[TOOL RESULT] {str(message.content)[:500]}")
    response=messages[-1].content

    if isinstance(response,str):
        response=clean_output(response)
    print("\nAgent: ",response)
    has_context=True