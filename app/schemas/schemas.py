import datetime as dt
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class ChunkingStrategy(str, Enum):
    fixed = "fixed"
    recursive = "recursive"


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunking_strategy: ChunkingStrategy
    chunk_count: int


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    booking_id: int | None = None


class BookingDetails(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    interview_date: dt.date
    interview_time: dt.time


class RetrievedChunk(BaseModel):
    text: str
    filename: str
    score: float