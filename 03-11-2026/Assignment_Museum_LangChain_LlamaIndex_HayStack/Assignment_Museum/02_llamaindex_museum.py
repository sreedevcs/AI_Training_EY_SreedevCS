from pathlib import Path

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

PROJECT_ROOT = Path(__file__).resolve().parent
from rag_core import DB_PATH, DOCUMENT_PATH

COLLECTION = "museum_llamaindex"

documents = SimpleDirectoryReader(
    input_files=[str(path) for path in DOCUMENT_PATH]
).load_data()

for document in documents:
    file_path = Path(document.metadata["file_path"]).resolve()
    document.metadata["source"] = str(file_path.relative_to(PROJECT_ROOT))

print("Documents loaded:", ", ".join(document.metadata["source"] for document in documents))

splitter = SentenceSplitter(
    chunk_size=150,
    chunk_overlap=20
)

nodes = splitter.get_nodes_from_documents(documents)

print("Total nodes:", len(nodes))
# print("First node:", nodes[0].get_content()[:150])

embedding_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

DB_PATH.mkdir(exist_ok=True)
client = chromadb.PersistentClient(path=str(DB_PATH))

# Rebuild only the LlamaIndex collection on each execution.
existing_names = [c.name for c in client.list_collections()]

if COLLECTION in existing_names:
    client.delete_collection(COLLECTION)

collection = client.get_or_create_collection(COLLECTION)

vector_store = ChromaVectorStore(
    chroma_collection=collection
)

storage = StorageContext.from_defaults(
    vector_store=vector_store
)

index = VectorStoreIndex(
    nodes,
    storage_context=storage,
    embed_model=embedding_model
)

print("Stored nodes:", collection.count())

retriever = index.as_retriever(similarity_top_k=2)

while True:
    question = input("\nQuestion (exit to stop): ").strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    results = retriever.retrieve(question)

    for i, result in enumerate(results, start=1):
        print("\n" + "=" * 120)
        print("Result:", i)
        print("Source:", result.node.metadata.get("source", "unknown"))
        print("Node ID:", result.node.node_id)
        print("Relevance score:", result.score)
        print("Text:", result.node.get_content())
