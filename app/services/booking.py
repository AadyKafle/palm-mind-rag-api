import datetime as dt
import json

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.models import BookingRecord
from app.schemas.schemas import BookingDetails
from app.services.llm import ChatMessage, LLMClient
from app.services.memory import ChatMemory

FIELDS = ("name", "email", "interview_date", "interview_time")

EXTRACTION_PROMPT = """You extract interview-booking details from a chat.
Today's date is {today}.
Current partially collected details: {draft}
A booking is currently in progress: {in_progress}

Return ONLY a JSON object with these keys:
- "wants_booking": true if the user wants to book an interview OR is continuing
  an in-progress booking; false otherwise (e.g. they ask an unrelated question).
- "name": full name or null
- "email": email or null
- "interview_date": date as YYYY-MM-DD or null (resolve "tomorrow", "next Monday")
- "interview_time": time as HH:MM in 24h format or null
Only include values the user actually stated. Use null for anything unknown."""


class BookingResult:
    def __init__(self, reply: str, booking_id: int | None = None) -> None:
        self.reply = reply
        self.booking_id = booking_id


class BookingService:
    def __init__(self, llm: LLMClient, memory: ChatMemory) -> None:
        self._llm = llm
        self._memory = memory

    def _extract(
        self, message: str, history: list[ChatMessage], draft: dict[str, str]
    ) -> dict:
        system = EXTRACTION_PROMPT.format(
            today=dt.date.today().isoformat(),
            draft=json.dumps(draft),
            in_progress=bool(draft),
        )
        transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history[-6:])
        raw = self._llm.chat(
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"Recent chat:\n{transcript}\n\nLatest message: {message}",
                },
            ],
            json_mode=True,
            temperature=0.0,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"wants_booking": False}

    def process(
        self,
        db: Session,
        session_id: str,
        message: str,
        history: list[ChatMessage],
    ) -> BookingResult | None:
        """Returns a result if the message belongs to the booking flow, else None."""
        draft = self._memory.get_draft(session_id)
        extracted = self._extract(message, history, draft)

        if not extracted.get("wants_booking"):
            if draft:
                self._memory.clear_draft(session_id)
            return None

        for field in FIELDS:
            value = extracted.get(field)
            if value:
                draft[field] = str(value)

        missing = [f for f in FIELDS if not draft.get(f)]
        if missing:
            self._memory.set_draft(session_id, draft)
            readable = ", ".join(f.replace("_", " ") for f in missing)
            return BookingResult(
                f"Happy to book your interview! I still need your: {readable}."
            )

        try:
            details = BookingDetails(**draft)  # type: ignore[arg-type]
        except ValidationError as exc:
            bad = {str(err["loc"][0]) for err in exc.errors() if err["loc"]}
            for field in bad:
                draft.pop(field, None)
            self._memory.set_draft(session_id, draft)
            readable = ", ".join(f.replace("_", " ") for f in bad)
            return BookingResult(
                f"I couldn't understand your {readable}. Could you provide it again?"
            )

        record = BookingRecord(
            session_id=session_id,
            name=details.name,
            email=str(details.email),
            interview_date=details.interview_date,
            interview_time=details.interview_time,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        self._memory.clear_draft(session_id)

        return BookingResult(
            f"Your interview is booked, {details.name}! "
            f"Date: {details.interview_date}, time: {details.interview_time:%H:%M}. "
            f"A confirmation will go to {details.email}.",
            booking_id=record.id,
        )