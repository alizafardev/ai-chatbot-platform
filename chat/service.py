from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from core.rag.llm import get_llm


class ChatService:
    def __init__(self) -> None:
        self._prompt = ChatPromptTemplate.from_messages([("human", "{question}")])
        self._chain = self._prompt | get_llm() | StrOutputParser()

    def ask_question(self, question: str) -> dict:
        answer = self._chain.invoke({"question": question})
        return {
            "question": question,
            "answer": answer,
        }


chat_service = ChatService()
