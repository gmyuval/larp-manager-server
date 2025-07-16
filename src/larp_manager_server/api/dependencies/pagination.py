"""
Pagination dependencies for LARP Manager Server.

This module provides FastAPI dependencies for pagination functionality.
"""


class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(self, page: int = 1, size: int = 20, max_size: int = 100):
        """
        Initialize pagination parameters.
        
        Args:
            page: Page number (1-based)
            size: Number of items per page
            max_size: Maximum allowed page size
        """
        self.page = max(1, page)
        self.size = min(max_size, max(1, size))
        self.offset = (self.page - 1) * self.size
        self.limit = self.size
    
    def get_offset(self) -> int:
        """Get offset for database queries."""
        return self.offset
    
    def get_limit(self) -> int:
        """Get limit for database queries."""
        return self.limit
    
    def get_page_info(self, total_items: int) -> dict:
        """
        Get pagination information for response.
        
        Args:
            total_items: Total number of items
            
        Returns:
            Dictionary containing pagination metadata
        """
        total_pages = (total_items + self.size - 1) // self.size
        
        return {
            "page": self.page,
            "size": self.size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": self.page < total_pages,
            "has_previous": self.page > 1,
        }


def get_pagination_params(
    page: int = 1,
    size: int = 20
) -> PaginationParams:
    """
    Get pagination parameters dependency.
    
    This dependency extracts pagination parameters from query parameters
    and returns a validated PaginationParams object.
    
    Args:
        page: Page number (1-based)
        size: Number of items per page
        
    Returns:
        PaginationParams object with validated parameters
    """
    return PaginationParams(page=page, size=size)