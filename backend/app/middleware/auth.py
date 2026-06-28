"""Authentication middleware — JWT verification via Supabase."""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_supabase
from app.utils.logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Extract and verify the JWT from the Authorization header.
    Returns the authenticated user dict from Supabase.
    
    Raises HTTPException 401 if token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid access token.",
        )

    token = credentials.credentials
    supabase = get_supabase()

    if supabase is None:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable. Supabase not configured.",
        )

    try:
        # Verify the JWT and get user data
        user_response = supabase.auth.get_user(token)
        
        if user_response is None or user_response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token.",
            )
        
        user = user_response.user
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.user_metadata.get("full_name", ""),
            "access_token": token,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict | None:
    """
    Same as get_current_user but returns None instead of raising
    if no token is provided. Useful for endpoints that work
    both authenticated and unauthenticated.
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(
            request=None,
            credentials=credentials,
        )
    except HTTPException:
        return None
