"""
Error handling classes for LARP Manager Server.

This module provides custom exception classes for API error handling.
"""

from typing import Optional

from fastapi import status


class APIError(Exception):
    """
    Base API error class.
    
    This is the base class for all API-related exceptions.
    """
    
    def __init__(self, status_code: int, detail: str, headers: Optional[dict] = None):
        """
        Initialize API error.
        
        Args:
            status_code: HTTP status code
            detail: Error detail message
            headers: Optional HTTP headers
        """
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


class ValidationError(APIError):
    """
    Validation error for invalid input data.
    
    This exception is raised when request data fails validation.
    """
    
    def __init__(self, detail: str, field: Optional[str] = None):
        """
        Initialize validation error.
        
        Args:
            detail: Error detail message
            field: Optional field name that caused the error
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
        self.field = field


class NotFoundError(APIError):
    """
    Not found error for missing resources.
    
    This exception is raised when a requested resource is not found.
    """
    
    def __init__(self, resource: str, identifier: str):
        """
        Initialize not found error.
        
        Args:
            resource: Name of the resource type
            identifier: Identifier of the resource that was not found
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' not found"
        )
        self.resource = resource
        self.identifier = identifier


class ConflictError(APIError):
    """
    Conflict error for resource conflicts.
    
    This exception is raised when a request conflicts with the current
    state of a resource.
    """
    
    def __init__(self, detail: str):
        """
        Initialize conflict error.
        
        Args:
            detail: Error detail message
        """
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class UnauthorizedError(APIError):
    """
    Unauthorized error for authentication failures.
    
    This exception is raised when authentication is required but not provided
    or invalid.
    """
    
    def __init__(self, detail: str = "Authentication required"):
        """
        Initialize unauthorized error.
        
        Args:
            detail: Error detail message
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ForbiddenError(APIError):
    """
    Forbidden error for authorization failures.
    
    This exception is raised when the user is authenticated but doesn't
    have permission to access the resource.
    """
    
    def __init__(self, detail: str = "Insufficient permissions"):
        """
        Initialize forbidden error.
        
        Args:
            detail: Error detail message
        """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )