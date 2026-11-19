from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.schemas.schemas import RetrievedChunk


class VectorStore:
    """Qdrant wrapper. Uses a remote server if QDRANT_URL is set, else local disk."""

    def __init__(self) -> None:
        if settings.qdrant_url:
            self._client = QdrantClient(
                url=settings.qdrant_url, api_key=settings.qdrant_api_key
            )
        else:
            self._client = QdrantClient(path=settings.qdrant_path)

        if not self._client.collection_exists(settings.qdrant_collection):
            self._client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dim, distance=Distance.COSINE
                ),
            )

    def upsert_chunks(
        self,
        document_id: str,
        filename: str,
        chunks: list[str],
        vectors: list[list[float]],
    ) -> None:
        points = [
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": index,
                    "text": chunk,
                },
            )
            for index, (chunk, vector) in enumerate(zip(chunks, vectors))
        ]
        self._client.upsert(collection_name=settings.qdrant_collection, points=points)

    def search(self, vector: list[float], top_k: int) -> list[RetrievedChunk]:
        result = self._client.query_points(
            collection_name=settings.qdrant_collection,
            query=vector,
            limit=top_k,
            with_payload=True,
        )
        return [
            RetrievedChunk(
                text=str((p.payload or {}).get("text", "")),
                filename=str((p.payload or {}).get("filename", "")),
                score=p.score,
            )
            for p in result.points
        ]