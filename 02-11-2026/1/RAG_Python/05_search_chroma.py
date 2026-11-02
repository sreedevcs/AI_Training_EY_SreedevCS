from rag_core import search_chunks

question = input("\nEnter your question: ")

results = search_chunks(question, top_k=2)

print("\n" + "=" * 70)
print("USER QUESTION:", question)
print("=" * 70)

for i, result in enumerate(results, start=1):

    print(f"\nRESULT {i}")
    print("-" * 70)

    print("Chunk ID:", result["id"])
    print("Source:", result["source"])
    print("Cosine Distance:", round(result["distance"], 4))

    print("\nRetrieved Text:")
    print(result["text"])

print("\n" + "=" * 70)
print("Total chunks retrieved:", len(results))
