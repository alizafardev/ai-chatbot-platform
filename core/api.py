import os

from django.utils import timezone
from ninja import Router, Schema

router = Router(tags=["core"])


class PingResponse(Schema):
    status: str
    service: str
    timestamp: str
    environment: str


@router.get("/ping", response=PingResponse)
def ping(request):
    return {
        "status": "ok",
        "service": "ai-chatbot-platform",
        "timestamp": timezone.now().isoformat(),
        "environment": "heroku" if os.environ.get("DYNO") else "local",
    }
