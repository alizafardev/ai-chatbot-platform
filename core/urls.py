import os

from django.http import JsonResponse
from django.urls import path
from django.utils import timezone


def health(request):
    return JsonResponse({"status": "ok"})


def api_ping(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "ai-chatbot-platform",
            "endpoint": "/api/ping/",
            "method": request.method,
            "timestamp": timezone.now().isoformat(),
            "environment": "heroku" if os.environ.get("DYNO") else "local",
        }
    )


urlpatterns = [
    path("health/", health, name="health"),
    path("api/ping/", api_ping, name="api-ping"),
]
