from rag_core import TOKENIZER, read_all_documents

documents = read_all_documents()

total_tokens = 0

for filename, text in documents.items():

    token_ids = TOKENIZER.encode(text)

    print("=" * 70)
    print("DOCUMENT:", filename)
    print("Character count:", len(text))
    print("Token count:", len(token_ids))

    print("\nFIRST 20 TOKEN IDs:")
    print(token_ids[:20])

    total_tokens += len(token_ids)

print("\n" + "=" * 70)
print("TOTAL DOCUMENTS:", len(documents))
print("TOTAL TOKENS:", total_tokens)
