
"""STEP 3 - Chunk both documents and generate embeddings."""

from rag_core import read_all_documents, make_chunks, embed_texts, TOKENIZER

documents = read_all_documents()

total_chunks = 0

for filename, text in documents.items():

    print("\n" + "=" * 70)
    print("DOCUMENT:", filename)

    # Split document into chunks
    chunks = make_chunks(text, chunk_size=120, overlap=20)

    print("Total chunks:", len(chunks))

    total_chunks += len(chunks)

    print("\nSample chunk:")
    print("-" * 70)
    print(chunks[0] if chunks else "No chunks generated")

    # Generate embeddings
    vectors = embed_texts(chunks)

    print("\nNumber of embeddings:", len(vectors))

    if vectors:
        print("Embedding vector size:", len(vectors[0]))

        print("First 8 vector values:",
              [round(x, 4) for x in vectors[0][:8]])

    print("\nChunk token counts:")

    for i, chunk in enumerate(chunks, start=1):
        token_count = len(TOKENIZER.encode(chunk))
        print(f"Chunk {i}: {token_count} tokens")

print("\n" + "=" * 70)
print("TOTAL CHUNKS FROM BOTH DOCUMENTS:", total_chunks)
print("Expected embedding dimension: 384")
