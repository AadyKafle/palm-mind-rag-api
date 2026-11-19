from functools import lru_cache

from app.services.booking import BookingService
from app.services.ingestion import IngestionService
from app.services.llm import LLMClient
from app.services.memory import ChatMemory
from app.services.rag import RAGService
from app.services.vector_store import VectorStore


@lru_cache
def get_llm() -> LLMClient:
    return LLMClient()


@lru_cache
def get_store() -> VectorStore:
    return VectorStore()


@lru_cache
def get_memory() -> ChatMemory:
    return ChatMemory()


@lru_cache
def get_ingestion_service() -> IngestionService:
    return IngestionService(get_llm(), get_store())


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService(get_llm(), get_store())


@lru_cache
def get_booking_service() -> BookingService:
    return BookingService(get_llm(), get_memory())