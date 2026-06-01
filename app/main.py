import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.utils.logger import setup_logger
from app.db.session import engine, Base
from app.api import health, documents, chat, auth

# Load environment variables
load_dotenv()

# Setup app-level logger
app_logger = setup_logger("app_main")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pinecone Assistant Multi-User RAG API",
    description="A production-grade multi-user backend for Pinecone Assistant with PDF/Doc chat capabilities.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request/response logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    app_logger.info(f"Incoming request: {method} {path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        status_code = response.status_code
        
        app_logger.info(
            f"Request completed: {method} {path} | "
            f"Status: {status_code} | "
            f"Time: {process_time:.4f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        app_logger.exception(
            f"Request failed: {method} {path} | "
            f"Error: {str(e)} | "
            f"Time: {process_time:.4f}s"
        )
        raise e

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.on_event("startup")
async def startup_event():
    app_logger.info("Application is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("Application is shutting down...")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Pinecone Assistant Multi-User RAG API",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    app_logger.info("Starting Uvicorn server on port 5000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)
