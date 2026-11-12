
"""Shared configuration and RAG functions."""

from pathlib import Path
import chromadb
import tiktoken
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = PROJECT_DIR / "Documents"

DOCUMENT_PATHS = [
    DOCUMENTS_DIR / "Employee_Workplace_Policy.txt",
    DOCUMENTS_DIR / "IT_Help_Desk_Guide.txt"
]

DB_PATH = PROJECT_DIR / "chroma_db"

COLLECTION_NAME = "company_documents"


# Tokenizer for counting and splitting text
TOKENIZER = tiktoken.get_encoding("cl100k_base")


# Embedding model
EMBEDDING_MODEL = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# READ DOCUMENTS
# --------------------------------------------------

def read_document(document_path):
    """Read a text document."""

    if not document_path.exists():
        raise FileNotFoundError(f"File not found: {document_path}")

    return document_path.read_text(encoding="utf-8")


def read_all_documents():
    """Read both source documents."""

    documents = {}

    for path in DOCUMENT_PATHS:
        documents[path.name] = read_document(path)

    return documents


# --------------------------------------------------
# CHUNKING
# --------------------------------------------------

def make_chunks(text, chunk_size=120, overlap=20):
    """Split text into token-based chunks with overlap."""

    if not (0 <= overlap < chunk_size):
        raise ValueError(
            "Overlap must be >= 0 and smaller than chunk_size"
        )

    token_ids = TOKENIZER.encode(text)
    chunks = []
    start = 0

    while start < len(token_ids):

        end = min(start + chunk_size, len(token_ids))

        chunk = TOKENIZER.decode(token_ids[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(token_ids):
            break

        start = end - overlap

    return chunks


# --------------------------------------------------
# EMBEDDINGS
# --------------------------------------------------

def embed_texts(texts):
    """Convert text into 384-dimensional embedding vectors."""

    vectors = EMBEDDING_MODEL.encode(texts)

    return vectors.tolist()


# --------------------------------------------------
# CHROMADB
# --------------------------------------------------

def get_database():
    """Return persistent ChromaDB client."""

    return chromadb.PersistentClient(path=str(DB_PATH))


# --------------------------------------------------
# SEMANTIC SEARCH
# --------------------------------------------------

def search_chunks(question, top_k=2):
    """Find the most relevant document chunks."""

    db = get_database()

    try:
        collection = db.get_collection(
            COLLECTION_NAME,
            embedding_function=None
        )

    except Exception as exc:
        raise RuntimeError(
            "No indexed collection. Run 04_store_in_chroma.py first."
        ) from exc

    count = collection.count()

    if count == 0:
        raise RuntimeError("The collection is empty.")

    question_vector = embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[question_vector],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for chunk_id, text, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):

        matches.append({
            "id": chunk_id,
            "text": text,
            "source": metadata.get("source", "unknown"),
            "distance": distance
        })

    return matches
