from app.core.config import settings
from app.services.llm import ChatMessage, LLMClient
from app.services.vector_store import VectorStore

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer using ONLY the provided context. "
    "If the answer is not in the context, say you don't know. "
    "Be concise."
)

REWRITE_PROMPT = (
    "Given the conversation and the latest user question, rewrite the question "
    "as a standalone question that can be understood without the conversation. "
    "Return only the rewritten question."
)


class RAGService:
    def __init__(self, llm: LLMClient, store: VectorStore) -> None:
        self._llm = llm
        self._store = store

    def _standalone_question(self, question: str, history: list[ChatMessage]) -> str:
        if not history:
            return question
        transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history)
        return self._llm.chat(
            [
                {"role": "system", "content": REWRITE_PROMPT},
                {
                    "role": "user",
                    "content": f"Conversation:\n{transcript}\n\nQuestion: {question}",
                },
            ],
            temperature=0.0,
        ).strip()

    def answer(self, question: str, history: list[ChatMessage]) -> str:
        standalone = self._standalone_question(question, history)
        vector = self._llm.embed([standalone])[0]
        chunks = self._store.search(vector, settings.top_k)

        if not chunks:
            context = "(no documents available)"
        else:
            context = "\n\n".join(
                f"[{i + 1}] ({c.filename}) {c.text}" for i, c in enumerate(chunks)
            )

        messages: list[ChatMessage] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ]
        return self._llm.chat(messages)