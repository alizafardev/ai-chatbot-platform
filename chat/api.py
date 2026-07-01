from ninja import Router, Schema

router = Router(tags=["chat"])


class ChatStatusResponse(Schema):
    status: str
    app: str


@router.get("/", response=ChatStatusResponse)
def chat_status(request):
    return {"status": "ok", "app": "chat"}
