from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.models import DocumentRecord
from app.schemas.schemas import ChunkingStrategy, UploadResponse
from app.services.chunking import fixed_size_chunking, recursive_chunking
from app.services.document import extract_pdf_text, extract_txt_text
from app.services.llm import LLMClient
from app.services.vector_store import VectorStore


class EmptyDocumentError(Exception):
    """Raised when no text could be extracted from the file."""


class IngestionService:
    def __init__(self, llm: LLMClient, store: VectorStore) -> None:
        self._llm = llm
        self._store = store

    def ingest(
        self,
        db: Session,
        filename: str,
        suffix: str,
        content: bytes,
        strategy: ChunkingStrategy,
    ) -> UploadResponse:
        document_id = str(uuid4())
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        path = upload_dir / f"{document_id}{suffix}"
        path.write_bytes(content)

        text = (
            extract_pdf_text(str(path))
            if suffix == ".pdf"
            else extract_txt_text(str(path))
        )

        chunker = (
            fixed_size_chunking
            if strategy == ChunkingStrategy.fixed
            else recursive_chunking
        )
        chunks = chunker(text)
        if not chunks:
            raise EmptyDocumentError("No text could be extracted from the document.")

        vectors = self._llm.embed(chunks)
        self._store.upsert_chunks(document_id, filename, chunks, vectors)

        db.add(
            DocumentRecord(
                id=document_id,
                filename=filename,
                file_type=suffix.lstrip("."),
                chunking_strategy=strategy.value,
                chunk_count=len(chunks),
            )
        )
        db.commit()

        return UploadResponse(
            document_id=document_id,
            filename=filename,
            chunking_strategy=strategy,
            chunk_count=len(chunks),
        )