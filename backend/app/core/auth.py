from fastapi import Header, HTTPException, status
from typing import Optional
from app.core.firebase import verify_token, get_user


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get the current authenticated user from Firebase token.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"message": f"Hello {user['email']}"}
    
    Args:
        authorization: The Authorization header containing Bearer token
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify token
        decoded_token = verify_token(token)
        
        # Get user information
        user = get_user(decoded_token["uid"])
        
        return user
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get the current user if authenticated, or None if not.
    Useful for routes that work with or without authentication.
    
    Args:
        authorization: The Authorization header containing Bearer token
        
    Returns:
        User information dictionary or None
    """
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        
        decoded_token = verify_token(token)
        user = get_user(decoded_token["uid"])
        return user
        
    except Exception:
        return None
