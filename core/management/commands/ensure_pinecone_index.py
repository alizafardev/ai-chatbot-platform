from django.core.management.base import BaseCommand

from core.rag.vectorstore import ensure_index


class Command(BaseCommand):
    help = "Create the Pinecone index if it does not exist."

    def handle(self, *args, **options):
        ensure_index()
        self.stdout.write(self.style.SUCCESS("Pinecone index is ready."))
