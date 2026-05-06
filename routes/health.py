from fastapi import APIRouter
from utils.response import success_response
from utils.logger import setup_logger
import os
import load_dotenv

load_dotenv.load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


router = APIRouter()
health_logger = setup_logger("health_route")

@router.get("/health")
async def health_check():
    health_logger.info("Health check endpoint hit")
    return success_response(message=f"Server running with PINECONE_API_KEY: {PINECONE_API_KEY}")
