from rag_core import (
    read_all_documents,
    make_chunks,
    embed_texts,
    get_database,
    COLLECTION_NAME
)

# Read both documents
documents = read_all_documents()

# Connect to persistent ChromaDB
db = get_database()

# Create or get collection
collection = db.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

# Prepare data for storage
all_chunks = []
all_embeddings = []
all_ids = []
all_metadata = []

chunk_counter = 0

for filename, text in documents.items():

    print("\nProcessing:", filename)

    # Split document into chunks
    chunks = make_chunks(text, chunk_size=120, overlap=20)

    # Generate embeddings
    embeddings = embed_texts(chunks)

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        chunk_id = f"chunk_{chunk_counter}"

        all_chunks.append(chunk)
        all_embeddings.append(embedding)
        all_ids.append(chunk_id)

        all_metadata.append({
            "source": filename,
            "chunk_number": i
        })

        chunk_counter += 1

    print("Chunks generated:", len(chunks))

# Store data in ChromaDB
if all_chunks:

    collection.upsert(
        ids=all_ids,
        documents=all_chunks,
        embeddings=all_embeddings,
        metadatas=all_metadata
    )

print("\n" + "=" * 60)
print("STORAGE COMPLETED")
print("Total chunks stored:", collection.count())
print("Collection name:", COLLECTION_NAME)
print("Database path:", db)
