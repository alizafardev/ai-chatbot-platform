from ninja import NinjaAPI

from chat.api import router as chat_router
from core.api import router as core_router

api = NinjaAPI(
    title="AI Chatbot Platform API",
    version="1.0.0",
    urls_namespace="api",
)

api.add_router("", core_router)
api.add_router("/chat", chat_router)
