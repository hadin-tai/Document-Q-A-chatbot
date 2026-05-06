from fastapi import APIRouter
from utils.response import success_response
from utils.logger import setup_logger

router = APIRouter()
health_logger = setup_logger("health_route")

@router.get("/health")
async def health_check():
    health_logger.info("Health check endpoint hit")
    return success_response(message="Server running")
