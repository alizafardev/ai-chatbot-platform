from ninja import Schema


class HelloRequest(Schema):
    question: str


class HelloResponse(Schema):
    question: str
    answer: str


class RagRequest(Schema):
    question: str


class RagResponse(Schema):
    question: str
    answer: str
    sources: list[str]
