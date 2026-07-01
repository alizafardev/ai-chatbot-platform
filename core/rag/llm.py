from django.conf import settings
from langchain_ollama import ChatOllama


def get_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.OLLAMA_LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
