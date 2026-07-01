from django.conf import settings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from core.rag.embeddings import get_embeddings


def _require_pinecone_api_key() -> None:
    if not settings.PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is not set")


def get_pinecone_client() -> Pinecone:
    _require_pinecone_api_key()
    return Pinecone(api_key=settings.PINECONE_API_KEY)


def ensure_index() -> None:
    client = get_pinecone_client()
    index_name = settings.PINECONE_INDEX_NAME

    if client.has_index(index_name):
        return

    client.create_index(
        name=index_name,
        dimension=settings.EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=settings.PINECONE_CLOUD,
            region=settings.PINECONE_REGION,
        ),
    )


def get_vectorstore() -> PineconeVectorStore:
    client = get_pinecone_client()
    index = client.Index(settings.PINECONE_INDEX_NAME)

    return PineconeVectorStore(
        index=index,
        embedding=get_embeddings(),
        namespace=settings.PINECONE_NAMESPACE,
    )
