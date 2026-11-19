from openai import OpenAI

from app.core.config import settings

ChatMessage = dict[str, str]


class LLMClient:
    """Thin wrapper around the OpenAI API (chat + embeddings)."""

    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.openai_api_key, base_url=settings.openai_base_url
        )

    def embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self._client.embeddings.create(
                model=settings.embedding_model, input=batch
            )
            vectors.extend(item.embedding for item in response.data)
        return vectors

    def chat(
        self,
        messages: list[ChatMessage],
        json_mode: bool = False,
        temperature: float = 0.2,
    ) -> str:
        kwargs: dict = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self._client.chat.completions.create(
            model=settings.chat_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content or ""