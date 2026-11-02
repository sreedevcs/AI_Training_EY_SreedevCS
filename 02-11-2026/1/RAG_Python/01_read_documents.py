from rag_core import read_all_documents, DOCUMENT_PATHS

documents = read_all_documents()

for filename, text in documents.items():

    print("=" * 70)
    print("DOCUMENT:", filename)
    print("Characters:", len(text))

    print("\nFIRST 700 CHARACTERS:\n")
    print(text[:700])

    print()

print("Total documents read:", len(documents))
