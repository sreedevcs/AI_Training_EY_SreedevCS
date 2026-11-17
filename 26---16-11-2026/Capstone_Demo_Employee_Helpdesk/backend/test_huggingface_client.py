
from app.ai.huggingface_client import get_llm


llm = get_llm()

response = llm.invoke(
    "Explain the difference between hardware and software issues in an IT helpdesk."
)

print("\nAI RESPONSE:")
print(response)
