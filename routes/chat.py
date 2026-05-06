from fastapi import APIRouter
from pydantic import BaseModel
from services.pinecone_service import pinecone_service
from utils.response import success_response, error_response
from utils.logger import setup_logger

router = APIRouter()
chat_logger = setup_logger("chat_route")

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
async def chat(request: ChatRequest):
    chat_logger.info(f"Chat request received. Question length: {len(request.question)}")
    
    if not request.question.strip():
        chat_logger.warning("Empty question received in chat request")
        return error_response("Question cannot be empty")

    try:
        chat_logger.info(f"Forwarding question to Pinecone service: {request.question[:50]}...")
        answer = await pinecone_service.chat(request.question)
        
        chat_logger.info("Successfully generated answer from Pinecone service")
        return success_response(
            data={
                "question": request.question,
                "answer": answer
            }
        )
    except Exception as e:
        chat_logger.exception(f"Unexpected error during chat processing: {str(e)}")
        return error_response(str(e), status_code=500)
