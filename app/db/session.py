import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Setup logging for database connection
logging.basicConfig(level=logging.INFO)
db_logger = logging.getLogger("db_session")

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    db_logger.error("DATABASE_URL not found in environment variables")
    raise ValueError("DATABASE_URL not found in environment variables")

db_logger.info(f"Connecting to database: {DATABASE_URL.split('@')[-1]}") # Log host part only for security

try:
    # Neon requires SSL, which is usually handled in the connection string (?sslmode=require)
    # We use psycopg2-binary as specified in requirements.txt
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True, # Ensure connection is alive
        pool_size=5,        # Adjust based on Neon tier
        max_overflow=10
    )
    
    # Test connection
    with engine.connect() as conn:
        db_logger.info("Successfully connected to Neon PostgreSQL")

except Exception as e:
    db_logger.exception(f"Failed to connect to Neon PostgreSQL: {str(e)}")
    raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
