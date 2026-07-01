from functools import lru_cache

from django.conf import settings
from openrouter import OpenRouter


def require_openrouter_api_key() -> None:
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set")


@lru_cache
def get_client() -> OpenRouter:
    require_openrouter_api_key()
    return OpenRouter(
        api_key=settings.OPENROUTER_API_KEY,
        http_referer=settings.OPENROUTER_SITE_URL or None,
        x_open_router_title=settings.OPENROUTER_SITE_NAME or None,
    )


def chat_complete(messages: list[dict]) -> str:
    response = get_client().chat.send(
        model=settings.OPENROUTER_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = get_client().embeddings.generate(
        input=texts,
        model=settings.OPENROUTER_EMBEDDING_MODEL,
    )
    return [item.embedding for item in response.data]
