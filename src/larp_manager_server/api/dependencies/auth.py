"""
Authentication dependencies for LARP Manager Server.

This module provides FastAPI dependencies for authentication and authorization.
Currently contains placeholders for Phase 2 implementation.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status

from larp_manager_server.api.dependencies.context import RequestContext, get_request_context


# Placeholder dependencies for future authentication system
async def get_current_user_optional(
    context: RequestContext = Depends(get_request_context)
) -> Optional[dict]:
    """
    Get current user (optional) dependency.
    
    This is a placeholder for the authentication system that will be
    implemented in Phase 2. Currently returns None.
    
    Args:
        context: Request context
        
    Returns:
        User information or None if not authenticated
    """
    # TODO: Implement in Phase 2
    return None


async def get_current_user_required(
    context: RequestContext = Depends(get_request_context)
) -> dict:
    """
    Get current user (required) dependency.
    
    This is a placeholder for the authentication system that will be
    implemented in Phase 2. Currently raises an exception.
    
    Args:
        context: Request context
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user is not authenticated
    """
    # TODO: Implement in Phase 2
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication not yet implemented"
    )


async def require_role(required_role: str):
    """
    Role-based access control dependency factory.
    
    This is a placeholder for the authorization system that will be
    implemented in Phase 2.
    
    Args:
        required_role: The role required to access the endpoint
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(
        user: dict = Depends(get_current_user_required)
    ) -> dict:
        # TODO: Implement in Phase 2
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization not yet implemented"
        )
    
    return role_checker


# Common role dependency factories (placeholders for Phase 2)
def get_user_role_dependency():
    """Get user role dependency."""
    return require_role("user")


def get_player_role_dependency():
    """Get player role dependency."""
    return require_role("player")


def get_gm_role_dependency():
    """Get GM role dependency."""
    return require_role("gm")


def get_admin_role_dependency():
    """Get admin role dependency."""
    return require_role("admin")