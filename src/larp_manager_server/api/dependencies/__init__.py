"""
Dependencies package for LARP Manager Server.

This package provides FastAPI dependencies organized into specialized modules:

- dependencies.database: Database-related dependencies
- dependencies.context: Request context dependencies  
- dependencies.auth: Authentication and authorization dependencies
- dependencies.pagination: Pagination dependencies
- dependencies.errors: Error handling classes

This __init__.py provides convenient imports for the most commonly used dependencies.
For specific functionality, import from the specialized modules directly.
"""

# Database dependencies
from larp_manager_server.api.dependencies.database import (
    get_db_session,
    get_db_session_with_error_handling,
)

# Context dependencies
from larp_manager_server.api.dependencies.context import (
    get_current_context,
    get_request_context,
    log_request_info,
    RequestContext,
)

# Authentication dependencies (placeholders for Phase 2)
from larp_manager_server.api.dependencies.auth import (
    get_current_user_optional,
    get_current_user_required,
    require_role,
    get_user_role_dependency,
    get_player_role_dependency,
    get_gm_role_dependency,
    get_admin_role_dependency,
)

# Pagination dependencies
from larp_manager_server.api.dependencies.pagination import (
    get_pagination_params,
    PaginationParams,
)

# Error handling classes
from larp_manager_server.api.dependencies.errors import (
    APIError,
    ValidationError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
)

# Common dependencies for convenience
__all__ = [
    # Database
    "get_db_session",
    "get_db_session_with_error_handling",
    
    # Context
    "get_current_context", 
    "get_request_context",
    "log_request_info",
    "RequestContext",
    
    # Auth (Phase 2 placeholders)
    "get_current_user_optional",
    "get_current_user_required",
    "require_role",
    "get_user_role_dependency",
    "get_player_role_dependency", 
    "get_gm_role_dependency",
    "get_admin_role_dependency",
    
    # Pagination
    "get_pagination_params",
    "PaginationParams",
    
    # Errors
    "APIError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
]