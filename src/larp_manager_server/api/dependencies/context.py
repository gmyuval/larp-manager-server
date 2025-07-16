"""
Request context dependencies for LARP Manager Server.

This module provides FastAPI dependencies for request context management.
"""

import logging
from typing import Optional

from fastapi import Depends, Request

logger = logging.getLogger(__name__)


def get_current_context(request: Request) -> dict:
    """
    Get current request context dependency.
    
    This dependency provides request context information that can be
    used throughout the request lifecycle.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        Dictionary containing request context information
    """
    return {
        "request_id": getattr(request.state, "request_id", None),
        "user_agent": request.headers.get("user-agent"),
        "client_ip": request.client.host if request.client else None,
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
    }


class RequestContext:
    """Request context manager for storing request-specific information."""
    
    def __init__(self, context: dict):
        self.context = context
        self.user_id: Optional[str] = None
        self.user_role: Optional[str] = None
        self.authenticated: bool = False
    
    def set_user_info(self, user_id: str, role: str) -> None:
        """Set user information in the context."""
        self.user_id = user_id
        self.user_role = role
        self.authenticated = True
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.authenticated
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID."""
        return self.user_id
    
    def get_user_role(self) -> Optional[str]:
        """Get current user role."""
        return self.user_role
    
    def get_client_ip(self) -> Optional[str]:
        """Get client IP address."""
        return self.context.get("client_ip")
    
    def get_request_id(self) -> Optional[str]:
        """Get request ID."""
        return self.context.get("request_id")


def get_request_context(
    context: dict = Depends(get_current_context)
) -> RequestContext:
    """
    Get request context object dependency.
    
    This dependency provides a RequestContext object that can be used
    to store and retrieve request-specific information.
    """
    return RequestContext(context)


async def log_request_info(
    context: RequestContext = Depends(get_request_context)
) -> None:
    """
    Log request information dependency.
    
    This dependency logs basic request information for debugging
    and monitoring purposes.
    """
    logger.info(
        f"Request: {context.context['method']} {context.context['path']} "
        f"from {context.get_client_ip()}"
    )