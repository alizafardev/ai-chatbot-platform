from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.rag.vectorstore import get_vectorstore


def _split_text(text: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    return splitter.split_text(text)


def ingest_text(text: str, metadata: dict | None = None) -> list[str]:
    """Chunk text, embed, and upsert into Pinecone. Returns document IDs."""
    docs = [
        Document(page_content=chunk, metadata=metadata or {})
        for chunk in _split_text(text)
    ]
    return get_vectorstore().add_documents(docs)


def search_similar(query: str, k: int = 4) -> list[Document]:
    """Return the top-k most similar documents for a query."""
    return get_vectorstore().similarity_search(query, k=k)
