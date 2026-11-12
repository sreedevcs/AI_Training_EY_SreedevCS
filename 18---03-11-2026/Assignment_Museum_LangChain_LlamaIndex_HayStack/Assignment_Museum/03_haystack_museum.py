from pathlib import Path

from haystack import Document,Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.sentence_transformers import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)

PROJECT_ROOT = Path(__file__).resolve().parent
from rag_core import DB_PATH, DOCUMENT_PATH
MODEL = "sentence-transformers/all-MiniLM-L6-v2"


documents = [
    Document(
        content=path.read_text(encoding="utf-8"),
        meta={"source": str(path.relative_to(PROJECT_ROOT))},
    )
    for path in DOCUMENT_PATH
]
print("Documents loaded:", ", ".join(doc.meta["source"] for doc in documents))
store = InMemoryDocumentStore(
    embedding_similarity_function="cosine"
)
indexing = Pipeline()

indexing.add_component(
    "splitter",
    DocumentSplitter(
        split_by="word",
        split_length=100,
        split_overlap=15
    )
)

indexing.add_component(
    "embedder",
    SentenceTransformersDocumentEmbedder(model=MODEL)
)

indexing.add_component(
    "writer",
    DocumentWriter(document_store=store)
)

indexing.connect(
    "splitter.documents",
    "embedder.documents"
)

indexing.connect(
    "embedder.documents",
    "writer.documents"
)

indexing.run({
    "splitter": {"documents": documents}
})

print("Stored chunks:", store.count_documents())

search = Pipeline()

search.add_component(
    "query_embedder",
    SentenceTransformersTextEmbedder(model=MODEL)
)

search.add_component(
    "retriever",
    InMemoryEmbeddingRetriever(
        document_store=store,
        top_k=2
    )
)

search.connect(
    "query_embedder.embedding",
    "retriever.query_embedding"
)

while True:

    question = input("\nQuestion (exit to stop): ").strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    result = search.run({
        "query_embedder": {"text": question}
    })

    chunks = result["retriever"]["documents"]

    for i, chunk in enumerate(chunks, start=1):

        print("\n" + "=" * 100)
        print("Result:", i)
        print("Source:", chunk.meta.get("source"))
        print("Similarity:", chunk.score)
        print("Text:", chunk.content)


