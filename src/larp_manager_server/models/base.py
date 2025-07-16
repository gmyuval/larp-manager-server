"""
Base model class for LARP Manager Server.

This module provides the base SQLAlchemy model class with common fields
and methods for all models in the application.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # Convert CamelCase to snake_case
        name = cls.__name__
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)
    
    @declared_attr
    def __table_args__(cls) -> Dict[str, Any]:
        """Set table arguments including schema."""
        return {'schema': 'larp_manager'}


class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now()
    )


class UUIDMixin:
    """Mixin for adding UUID primary key to models."""
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Base model class with UUID primary key and timestamp fields.
    
    This class provides common functionality for all models including:
    - UUID primary key
    - Created and updated timestamps
    - Schema assignment to 'larp_manager'
    - Common utility methods
    """
    
    __abstract__ = True
    
    def to_dict(self, exclude: Optional[set] = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Args:
            exclude: Set of column names to exclude from the dictionary
            
        Returns:
            Dictionary representation of the model
        """
        exclude = exclude or set()
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                # Convert datetime to ISO format string
                if isinstance(value, datetime):
                    value = value.isoformat()
                # Convert UUID to string
                elif isinstance(value, uuid.UUID):
                    value = str(value)
                result[column.name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude: Optional[set] = None) -> None:
        """
        Update model instance from dictionary.
        
        Args:
            data: Dictionary with updated values
            exclude: Set of column names to exclude from update
        """
        exclude = exclude or {'id', 'created_at', 'updated_at'}
        
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_column_names(cls) -> list[str]:
        """Get list of column names for the model."""
        return [column.name for column in cls.__table__.columns]
    
    @classmethod
    def get_required_columns(cls) -> list[str]:
        """Get list of required (non-nullable) column names."""
        return [
            column.name for column in cls.__table__.columns
            if not column.nullable and column.default is None
        ]
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.__class__.__name__}({self.id})"


class NamedModel(BaseModel):
    """
    Base model class with name field.
    
    This class extends BaseModel with a name field for models that
    need to be identified by a human-readable name.
    """
    
    __abstract__ = True
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    
    def __str__(self) -> str:
        """Human-readable string representation with name."""
        return f"{self.__class__.__name__}({self.name})"


class DescribedModel(NamedModel):
    """
    Base model class with name and description fields.
    
    This class extends NamedModel with a description field for models
    that need additional descriptive information.
    """
    
    __abstract__ = True
    
    description: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )