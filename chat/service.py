from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from core.rag import search_similar
from core.rag.llm import get_llm


class ChatService:
    def __init__(self) -> None:
        self._hello_prompt = ChatPromptTemplate.from_messages([("human", "{question}")])
        self._hello_chain = self._hello_prompt | get_llm() | StrOutputParser()

        self._rag_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Answer using only the context below. If the answer is not in the context, "
                    "say you don't know.\n\nContext:\n{context}",
                ),
                ("human", "{question}"),
            ]
        )
        self._rag_chain = self._rag_prompt | get_llm() | StrOutputParser()

    def ask_question(self, question: str) -> dict:
        answer = self._hello_chain.invoke({"question": question})
        return {
            "question": question,
            "answer": answer,
        }

    def ask_with_rag(self, question: str, k: int = 2) -> dict:
        docs = search_similar(question, k=k)

        if not docs:
            raise ValueError(
                "No matching documents found in Pinecone. "
                "Ingest knowledge first, e.g. run: python manage.py rag_smoke_test"
            )

        context = "\n\n".join(doc.page_content for doc in docs)
        answer = self._rag_chain.invoke({"context": context, "question": question})

        return {
            "question": question,
            "answer": answer,
            "sources": [doc.page_content for doc in docs],
        }


chat_service = ChatService()
