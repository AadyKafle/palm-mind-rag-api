from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_booking_service, get_memory, get_rag_service
from app.database.session import get_db
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.booking import BookingService
from app.services.memory import ChatMemory
from app.services.rag import RAGService

router = APIRouter(prefix="/api/v1/chat", tags=["Conversational RAG"])


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    memory: ChatMemory = Depends(get_memory),
    rag: RAGService = Depends(get_rag_service),
    booking: BookingService = Depends(get_booking_service),
) -> ChatResponse:
    history = memory.get_history(request.session_id)

    result = booking.process(db, request.session_id, request.message, history)
    if result is not None:
        answer, booking_id = result.reply, result.booking_id
    else:
        answer, booking_id = rag.answer(request.message, history), None

    memory.add_message(request.session_id, "user", request.message)
    memory.add_message(request.session_id, "assistant", answer)

    return ChatResponse(
        session_id=request.session_id, answer=answer, booking_id=booking_id
    )