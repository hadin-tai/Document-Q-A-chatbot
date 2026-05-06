import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pinecone_service import pinecone_service
from utils.response import success_response, error_response
from utils.logger import setup_logger

router = APIRouter()
upload_logger = setup_logger("upload_route")

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_logger.info(f"Upload request received for file: {file.filename}")
    
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        upload_logger.warning(f"File type {ext} not allowed for {file.filename}")
        return error_response(f"File type {ext} not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}")

    # Create temp directory if not exists
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        upload_logger.info(f"Saving temporary file: {temp_file_path}")
        # Save temp file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        file_size = os.path.getsize(temp_file_path)
        upload_logger.info(f"File size: {file_size} bytes")
        
        if file_size > MAX_FILE_SIZE:
            upload_logger.warning(f"File size {file_size} exceeds 10MB limit for {file.filename}")
            os.remove(temp_file_path)
            return error_response("File size exceeds 10MB limit")

        # Upload to Pinecone
        upload_logger.info(f"Forwarding {file.filename} to Pinecone service")
        await pinecone_service.upload_file(temp_file_path)

        upload_logger.info(f"Successfully processed upload for {file.filename}")
        return success_response(
            data={"filename": file.filename},
            message="File uploaded successfully"
        )
    except Exception as e:
        upload_logger.exception(f"Unexpected error during upload of {file.filename}: {str(e)}")
        return error_response(str(e), status_code=500)
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            upload_logger.info(f"Cleaning up temporary file: {temp_file_path}")
            os.remove(temp_file_path)

@router.get("/files")
async def list_files():
    upload_logger.info("Request to list all files")
    try:
        files = await pinecone_service.list_files()
        return success_response(data={"files": files})
    except Exception as e:
        upload_logger.exception(f"Error listing files: {str(e)}")
        return error_response(str(e), status_code=500)

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    upload_logger.info(f"Request to delete file: {file_id}")
    try:
        await pinecone_service.delete_file(file_id)
        return success_response(message="File deleted")
    except Exception as e:
        upload_logger.exception(f"Error deleting file {file_id}: {str(e)}")
        return error_response(str(e), status_code=500)
