from ninja import Router
from ninja.errors import HttpError

from chat.schemas import HelloRequest, HelloResponse
from chat.service import chat_service

router = Router(tags=["chat"])


@router.post("/hello", response=HelloResponse)
def hello(request, payload: HelloRequest):
    """LangChain hello world: send a question, get an answer from Ollama."""
    try:
        return chat_service.ask_question(payload.question)
    except Exception as exc:
        raise HttpError(503, f"LangChain hello failed: {exc}") from exc
