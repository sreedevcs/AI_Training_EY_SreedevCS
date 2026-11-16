from uuid import uuid4

from app.agent import ask_agent
from app.memory import check_redis

if not check_redis():
    raise SystemExit("Redis connection failed")

print("Redis connected successfully")
session_id = f"SESSION-{uuid4()}"
print("Travel Assistant")
while True:
    question = input("Employee: ")
    if question.lower() in ["exit", "quit"]:
        break
    answer = ask_agent(question, session_id)
    print("Assistant: ", answer)