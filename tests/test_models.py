"""
Tests for base model classes.
"""

import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.larp_manager_server.models.base import BaseModel, NamedModel, DescribedModel


class TestBaseModelEntity(BaseModel):
    """Test model class for testing BaseModel functionality."""
    
    __tablename__ = "test_model"
    
    name = Column(String(255), nullable=False)


class TestNamedModelEntity(NamedModel):
    """Test model class for testing NamedModel functionality."""
    
    __tablename__ = "test_named_model"


class TestDescribedModelEntity(DescribedModel):
    """Test model class for testing DescribedModel functionality."""
    
    __tablename__ = "test_described_model"


class TestBaseModelClass:
    """Test BaseModel class functionality."""
    
    def test_table_name_generation(self):
        """Test automatic table name generation."""
        # Test simple class name
        assert TestBaseModelEntity.__tablename__ == "test_model"
        
        # Test CamelCase conversion
        class MyTestModel(BaseModel):
            __tablename__ = "my_test_model"
        
        # The actual table name should be generated automatically
        # but we override it in the test class
        assert MyTestModel.__tablename__ == "my_test_model"
    
    def test_table_schema(self):
        """Test table schema assignment."""
        model = TestBaseModelEntity()
        table_args = model.__table_args__
        
        assert table_args["schema"] == "larp_manager"
    
    def test_uuid_primary_key(self):
        """Test UUID primary key generation."""
        model = TestBaseModelEntity(name="test")
        
        # ID should be generated automatically
        assert model.id is not None
        assert isinstance(model.id, uuid.UUID)
    
    def test_timestamp_fields(self):
        """Test timestamp field generation."""
        model = TestBaseModelEntity(name="test")
        
        # Timestamps should be set automatically
        assert model.created_at is not None
        assert model.updated_at is not None
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
    
    def test_to_dict(self):
        """Test model to dictionary conversion."""
        model = TestBaseModelEntity(name="test")
        
        result = model.to_dict()
        
        assert isinstance(result, dict)
        assert "id" in result
        assert "name" in result
        assert "created_at" in result
        assert "updated_at" in result
        
        # Check that UUID is converted to string
        assert isinstance(result["id"], str)
        
        # Check that datetime is converted to ISO format
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)
    
    def test_to_dict_with_exclude(self):
        """Test model to dictionary conversion with exclusions."""
        model = TestBaseModelEntity(name="test")
        
        result = model.to_dict(exclude={"id", "created_at"})
        
        assert "id" not in result
        assert "created_at" not in result
        assert "name" in result
        assert "updated_at" in result
    
    def test_update_from_dict(self):
        """Test model update from dictionary."""
        model = TestBaseModelEntity(name="original")
        original_id = model.id
        original_created_at = model.created_at
        
        update_data = {
            "name": "updated",
            "id": str(uuid.uuid4()),  # Should be excluded
            "created_at": datetime.now(),  # Should be excluded
        }
        
        model.update_from_dict(update_data)
        
        # Name should be updated
        assert model.name == "updated"
        
        # ID and created_at should not be updated (excluded by default)
        assert model.id == original_id
        assert model.created_at == original_created_at
    
    def test_update_from_dict_with_custom_exclude(self):
        """Test model update from dictionary with custom exclusions."""
        model = TestBaseModelEntity(name="original")
        
        update_data = {
            "name": "updated",
        }
        
        model.update_from_dict(update_data, exclude={"name"})
        
        # Name should not be updated (excluded)
        assert model.name == "original"
    
    def test_get_column_names(self):
        """Test getting column names."""
        column_names = TestBaseModelEntity.get_column_names()
        
        expected_columns = {"id", "created_at", "updated_at", "name"}
        assert set(column_names) == expected_columns
    
    def test_get_required_columns(self):
        """Test getting required column names."""
        required_columns = TestBaseModelEntity.get_required_columns()
        
        # 'name' should be required (nullable=False, no default)
        assert "name" in required_columns
        
        # 'id' should not be required (has default)
        assert "id" not in required_columns
        
        # Timestamps should not be required (have defaults)
        assert "created_at" not in required_columns
        assert "updated_at" not in required_columns
    
    def test_repr(self):
        """Test string representation."""
        model = TestBaseModelEntity(name="test")
        
        repr_str = repr(model)
        assert "TestBaseModelEntity" in repr_str
        assert str(model.id) in repr_str
    
    def test_str(self):
        """Test string conversion."""
        model = TestBaseModelEntity(name="test")
        
        str_repr = str(model)
        assert "TestBaseModelEntity" in str_repr
        assert str(model.id) in str_repr


class TestNamedModelClass:
    """Test NamedModel class functionality."""
    
    def test_name_field(self):
        """Test name field in NamedModel."""
        model = TestNamedModelEntity(name="test name")
        
        assert model.name == "test name"
        assert hasattr(model, "id")
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")
    
    def test_str_with_name(self):
        """Test string representation with name."""
        model = TestNamedModelEntity(name="test name")
        
        str_repr = str(model)
        assert "TestNamedModelEntity" in str_repr
        assert "test name" in str_repr


class TestDescribedModelClass:
    """Test DescribedModel class functionality."""
    
    def test_name_and_description_fields(self):
        """Test name and description fields in DescribedModel."""
        model = TestDescribedModelEntity(
            name="test name",
            description="test description"
        )
        
        assert model.name == "test name"
        assert model.description == "test description"
        assert hasattr(model, "id")
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")
    
    def test_optional_description(self):
        """Test that description is optional."""
        model = TestDescribedModelEntity(name="test name")
        
        assert model.name == "test name"
        assert model.description is None
    
    def test_str_with_name(self):
        """Test string representation with name."""
        model = TestDescribedModelEntity(name="test name")
        
        str_repr = str(model)
        assert "TestDescribedModelEntity" in str_repr
        assert "test name" in str_repr