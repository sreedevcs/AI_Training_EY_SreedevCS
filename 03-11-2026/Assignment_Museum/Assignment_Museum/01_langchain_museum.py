from pathlib import Path
import sys

# Import rag_core.py from our existing project
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from rag_core import (
    DB_PATH,
    DOCUMENT_PATH,
    embed_texts,
    get_database,
)

COLLECTION = "museum_langchain"


# Reuse our existing local embedding model
class LocalEmbeddings(Embeddings):

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return embed_texts(texts)

    def embed_query(self, text: str) -> list[float]:
        return embed_texts([text])[0]

documents = [
    Document(
        page_content=path.read_text(encoding="utf-8"),
        metadata={"source": str(path.relative_to(PROJECT_ROOT))}
    )
    for path in DOCUMENT_PATH
]

print("Documents loaded:", ", ".join(document.metadata["source"] for document in documents))

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=150,
    chunk_overlap=20
)

chunks = splitter.split_documents(documents)

for i, chunk in enumerate(chunks, start=1):
    chunk.metadata["chunk_id"] = f"lc_chunk_{i:03d}"

print("Total chunks:", len(chunks))
# if chunks:
#     print("First chunk:", chunks[0].page_content[:150])
# else:
#     print("No chunks were created.")

client = get_database()

# Use a separate collection to protect our original data
if COLLECTION in [item.name for item in client.list_collections()]:
    client.delete_collection(COLLECTION)

store = Chroma.from_documents(
    documents=chunks,
    embedding=LocalEmbeddings(),
    collection_name=COLLECTION,
    persist_directory=str(DB_PATH),
    collection_configuration={"hnsw": {"space": "cosine"}}
)

print("Stored chunks:", client.get_collection(COLLECTION).count())

while True:
    question = input("\nEnter your question (exit to stop): ").strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    results = store.similarity_search_with_score(question, k=2)

    for document, distance in results:
        print("\n" + "-" * 120)
        print("Chunk:", document.metadata["chunk_id"])
        print("Source:", document.metadata["source"])
        print("Cosine distance:", round(distance, 4))
        print("Text:", document.page_content)

