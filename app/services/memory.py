import json

import redis

from app.core.config import settings
from app.services.llm import ChatMessage


class ChatMemory:
    """Redis-backed chat history and booking draft per session."""

    def __init__(self) -> None:
        self._r = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    @staticmethod
    def _hist_key(session_id: str) -> str:
        return f"chat:{session_id}:history"

    @staticmethod
    def _draft_key(session_id: str) -> str:
        return f"chat:{session_id}:booking_draft"

    def get_history(self, session_id: str) -> list[ChatMessage]:
        raw = self._r.lrange(self._hist_key(session_id), 0, -1)
        return [json.loads(item) for item in raw]  # type: ignore[union-attr]

    def add_message(self, session_id: str, role: str, content: str) -> None:
        key = self._hist_key(session_id)
        self._r.rpush(key, json.dumps({"role": role, "content": content}))
        self._r.ltrim(key, -settings.history_limit, -1)
        self._r.expire(key, settings.chat_ttl_seconds)

    def get_draft(self, session_id: str) -> dict[str, str]:
        raw = self._r.get(self._draft_key(session_id))
        return json.loads(raw) if raw else {}  # type: ignore[arg-type]

    def set_draft(self, session_id: str, draft: dict[str, str]) -> None:
        self._r.set(
            self._draft_key(session_id),
            json.dumps(draft),
            ex=settings.chat_ttl_seconds,
        )

    def clear_draft(self, session_id: str) -> None:
        self._r.delete(self._draft_key(session_id))