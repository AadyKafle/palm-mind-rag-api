from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_ingestion_service
from app.database.session import get_db
from app.schemas.schemas import ChunkingStrategy, UploadResponse
from app.services.ingestion import EmptyDocumentError, IngestionService

router = APIRouter(prefix="/api/v1/documents", tags=["Document Ingestion"])

ALLOWED_SUFFIXES = {".pdf", ".txt"}


@router.post("/upload", response_model=UploadResponse, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkingStrategy = Form(ChunkingStrategy.recursive),
    db: Session = Depends(get_db),
    service: IngestionService = Depends(get_ingestion_service),
) -> UploadResponse:
    filename = file.filename or "unknown"
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt are supported.")

    content = file.file.read()
    try:
        return service.ingest(db, filename, suffix, content, chunking_strategy)
    except EmptyDocumentError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc