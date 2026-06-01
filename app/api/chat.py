from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageResponse
from app.services.pinecone_service import pinecone_service
from app.utils.logger import setup_logger

router = APIRouter()
chat_logger = setup_logger("chat_route")

@router.get("/{document_id}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch chat history for a specific document with ownership validation
    """
    chat_logger.info(f"Fetching chat history for user {current_user.id}, doc {document_id}")
    
    # Ownership validation
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    messages = db.query(ChatMessage).filter(
        ChatMessage.document_id == document_id,
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return messages

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat_logger.info(f"Chat request from user {current_user.id} for doc {request.document_id}")
    
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    # Ownership validation
    doc = db.query(Document).filter(
        Document.id == request.document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not doc:
        chat_logger.warning(f"Document {request.document_id} not found or not owned by user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    try:
        # Call Pinecone with strict metadata filter
        answer = await pinecone_service.chat(
            question=request.question,
            user_id=current_user.id,
            document_id=request.document_id
        )
        
        # Save chat message to DB (Optional but recommended)
        user_msg = ChatMessage(
            user_id=current_user.id,
            document_id=request.document_id,
            role="user",
            message=request.question
        )
        assistant_msg = ChatMessage(
            user_id=current_user.id,
            document_id=request.document_id,
            role="assistant",
            message=answer
        )
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()

        return ChatResponse(
            question=request.question,
            answer=answer,
            document_id=request.document_id
        )
    except Exception as e:
        chat_logger.exception(f"Unexpected error during chat processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
