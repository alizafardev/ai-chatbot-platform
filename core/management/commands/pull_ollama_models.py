import json

import httpx
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Pull Ollama models used for embeddings and chat."

    def handle(self, *args, **options):
        models = [settings.OLLAMA_EMBEDDING_MODEL, settings.OLLAMA_LLM_MODEL]

        for model in models:
            self.stdout.write(f"Pulling {model}...")
            self._pull_model(model)

        self.stdout.write(self.style.SUCCESS("Ollama models are ready."))

    def _pull_model(self, model: str) -> None:
        with httpx.Client(base_url=settings.OLLAMA_BASE_URL, timeout=None) as client:
            with client.stream("POST", "/api/pull", json={"name": model}) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    payload = json.loads(line)
                    status = payload.get("status", "")
                    if status:
                        self.stdout.write(status)
