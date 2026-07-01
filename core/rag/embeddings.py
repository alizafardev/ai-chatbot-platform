from django.conf import settings
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

from core.rag.openrouter import embed_texts, require_openrouter_api_key


class OpenRouterEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return embed_texts(texts)

    def embed_query(self, text: str) -> list[float]:
        return embed_texts([text])[0]


def get_embeddings() -> OllamaEmbeddings | OpenRouterEmbeddings:
    if settings.IS_HEROKU:
        require_openrouter_api_key()
        return OpenRouterEmbeddings()

    return OllamaEmbeddings(
        model=settings.OLLAMA_EMBEDDING_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
