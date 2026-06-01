import bcrypt
import logging
from fastapi import HTTPException, status

# ==========================================
# LOGGER CONFIGURATION
# ==========================================
logger = logging.getLogger("auth_utils")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hashed password.
    
    Args:
        plain_password: The raw password from the user.
        hashed_password: The hashed password stored in the database.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    if not plain_password or not hashed_password:
        return False

    try:
        # bcrypt.checkpw requires bytes
        # We ensure both are encoded to utf-8
        pw_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        
        return bcrypt.checkpw(pw_bytes, hash_bytes)

    except Exception as e:
        logger.error(f"Password verification runtime error: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """
    Generate a secure bcrypt hash for a plain text password.
    
    Args:
        password: The plain text password to hash.
        
    Returns:
        str: The generated bcrypt hash as a string.
        
    Raises:
        HTTPException: If password is empty or too long for bcrypt.
    """
    try:
        # Basic cleanup
        password = password.strip()
        
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot be empty"
            )

        # bcrypt has a 72-byte limit for the input password
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must not exceed 72 characters for security reasons"
            )

        # Generate salt and hash
        # gensalt() defaults to 12 rounds, which is the current industry standard for balance between speed and security
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        
        # Decode back to string for database storage
        return hashed_bytes.decode("utf-8")

    except HTTPException:
        # Re-raise known validation errors
        raise

    except Exception as e:
        # Log unexpected errors and raise a generic 500
        logger.exception(f"Unexpected error during password hashing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal security error occurred during password processing"
        )
