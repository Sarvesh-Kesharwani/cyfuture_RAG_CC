from fastapi import APIRouter
from pydantic import BaseModel
from backend.core.rag_chain import get_rag_response

router = APIRouter()


# Request schema
class ChatRequest(BaseModel):
    user_input: str


# Response schema
class ChatResponse(BaseModel):
    response: str


@router.post("/chatbot", response_model=ChatResponse)
def chatbot_endpoint(request: ChatRequest):
    user_message = request.user_input
    bot_reply = get_rag_response(user_message)
    return {"response": bot_reply}
