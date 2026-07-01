from ninja import Schema


class HelloRequest(Schema):
    question: str


class HelloResponse(Schema):
    question: str
    answer: str
