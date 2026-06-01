import logging
import sys

# Custom format for logs
LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"

def setup_logger(name: str):
    """
    Configures and returns a logger instance.
    """
    logger = logging.getLogger(name)
    
    # Set logging level (DEBUG for development, INFO for production)
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers if logger is already configured
    if not logger.handlers:
        # Stream handler for console output (Uvicorn terminal)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        
    return logger

# Create a root logger for the app
logger = setup_logger("pinecone_rag_app")
