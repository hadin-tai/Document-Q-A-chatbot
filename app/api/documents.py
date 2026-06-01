import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.pinecone_service import pinecone_service
from app.utils.response import success_response, error_response
from app.utils.logger import setup_logger

router = APIRouter()
doc_logger = setup_logger("documents_route")

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc_logger.info(f"Upload request from user {current_user.id} for file: {file.filename}")
    
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        doc_logger.warning(f"File type {ext} not allowed for {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {ext} not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Create uploads directory if not exists
    os.makedirs("uploads", exist_ok=True)
    
    # Generate internal document_id
    document_id = str(uuid.uuid4())
    temp_file_path = os.path.join("uploads", f"{document_id}_{file.filename}")

    try:
        # Save temp file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        file_size = os.path.getsize(temp_file_path)
        if file_size > MAX_FILE_SIZE:
            os.remove(temp_file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )

        # Upload to Pinecone with metadata isolation
        pinecone_response = await pinecone_service.upload_file(
            file_path=temp_file_path,
            user_id=current_user.id,
            document_id=document_id
        )

        # Save document record in PostgreSQL
        new_doc = Document(
            id=document_id,
            user_id=current_user.id,
            file_name=file.filename,
            pinecone_file_id=pinecone_response.id,
            upload_status="completed"
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        doc_logger.info(f"Successfully processed upload for {file.filename}, internal_id: {document_id}")
        return new_doc

    except Exception as e:
        doc_logger.exception(f"Unexpected error during upload of {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc_logger.info(f"Listing documents for user {current_user.id}")
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    return docs

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc_logger.info(f"Delete request for doc {document_id} from user {current_user.id}")
    
    # Ownership validation
    doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user.id
    ).first()
    
    if not doc:
        doc_logger.warning(f"Document {document_id} not found or not owned by user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    try:
        # Delete from Pinecone
        await pinecone_service.delete_file(doc.pinecone_file_id, current_user.id)
        
        # Delete from DB
        db.delete(doc)
        db.commit()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        doc_logger.exception(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
