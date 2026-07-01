from django.core.management.base import BaseCommand

from core.rag.ingest import ingest_text, search_similar
from core.rag.vectorstore import ensure_index


class Command(BaseCommand):
    help = "Embed, upsert, and query a test document in Pinecone."

    def handle(self, *args, **options):
        test_text = "The chatbot platform uses Pinecone for vector search."
        test_query = "What vector database does the platform use?"

        ensure_index()
        doc_ids = ingest_text(test_text, metadata={"source": "rag_smoke_test"})
        results = search_similar(test_query, k=1)

        if not results:
            self.stderr.write(self.style.ERROR("Smoke test failed: no search results."))
            return

        self.stdout.write(self.style.SUCCESS("RAG smoke test passed."))
        self.stdout.write(f"Upserted {len(doc_ids)} chunk(s).")
        self.stdout.write(f"Top result: {results[0].page_content}")
