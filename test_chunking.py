
from app.services.chunking import (
    fixed_size_chunking,
    recursive_chunking
)

sample_text = """
Palm Mind AI is building an intelligent document assistant.

The assistant uses Retrieval Augmented Generation (RAG).
Documents are extracted, divided into chunks, and converted
into vector embeddings.

The embeddings are stored in a vector database.
When users ask questions, relevant document chunks are retrieved.
The language model uses those chunks to generate answers.
"""

fixed_chunks = fixed_size_chunking(
    sample_text,
    chunk_size=100,
    overlap=20
)

recursive_chunks = recursive_chunking(
    sample_text,
    chunk_size=100,
    overlap=20
)

print("\n===== FIXED SIZE CHUNKS =====")
for i, chunk in enumerate(fixed_chunks):
    print(f"\nChunk {i + 1}: {chunk}")

print("\n===== RECURSIVE CHUNKS =====")
for i, chunk in enumerate(recursive_chunks):
    print(f"\nChunk {i + 1}: {chunk}")
