from django.conf import settings
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama

from core.rag.openrouter import chat_complete

_ROLE_MAP = {"human": "user", "ai": "assistant", "system": "system"}


def _to_openrouter_messages(prompt_value) -> list[dict]:
    return [
        {"role": _ROLE_MAP.get(message.type, message.type), "content": message.content}
        for message in prompt_value.to_messages()
    ]


def _invoke_openrouter(prompt_value) -> AIMessage:
    messages = _to_openrouter_messages(prompt_value)
    return AIMessage(content=chat_complete(messages))


def get_llm() -> ChatOllama | RunnableLambda:
    if settings.IS_HEROKU:
        return RunnableLambda(_invoke_openrouter)

    return ChatOllama(
        model=settings.OLLAMA_LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
