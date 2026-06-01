from fastapi import APIRouter
from app.utils.response import success_response
from app.utils.logger import setup_logger
import os

router = APIRouter()
health_logger = setup_logger("health_route")

@router.get("")
async def health_check():
    health_logger.info("Health check endpoint hit")
    return success_response(message="Server running")
