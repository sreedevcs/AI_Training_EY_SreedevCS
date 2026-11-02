from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

from rag_core import search_chunks


# Load environment variables
load_dotenv()

# Initialize AI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")

# Maximum acceptable cosine distance
MAX_DISTANCE = 0.45


def generate_answer(question):
    """Generate an answer using only retrieved document context."""

    # Retrieve top 2 relevant chunks
    results = search_chunks(question, top_k=2)

    if not results:
        return "I cannot find the answer in the provided documents."

    # Check whether retrieved chunks are sufficiently relevant
    if all(result["distance"] > MAX_DISTANCE for result in results):
        return "I cannot find the answer in the provided documents."

    # Construct context from retrieved chunks
    context = ""

    for result in results:
        context += (
            f"\nSource: {result['source']}\n"
            f"Chunk ID: {result['id']}\n"
            f"Content: {result['text']}\n"
        )

    # Construct prompt
    prompt = f"""
You are a document-based question answering assistant.

Answer the user's question using ONLY the information
provided in the context below.

Rules:
1. Do not use external knowledge.
2. Do not make assumptions or invent information.
3. If the answer is not explicitly available in the context,
   respond exactly:
   "I cannot find the answer in the provided documents."
4. Keep the answer concise and factual.

Context:
{context}

Question:
{question}

Answer:
"""

    # Generate response using the LLM
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


# Main program
if __name__ == "__main__":

    print("=" * 60)
    print("COMPANY DOCUMENT RAG ASSISTANT")
    print("=" * 60)

    while True:

        question = input("\nAsk your question (type 'exit' to quit): ")

        if question.lower().strip() == "exit":
            print("Exiting RAG assistant...")
            break

        answer = generate_answer(question)

        print("\nAI ANSWER:")
        print("-" * 60)
        print(answer)
        print("-" * 60)
