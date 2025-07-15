# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Create conda environment
conda env create -f environment.yml
conda activate larp-manager-server

# Or using pip
pip install -r requirements-dev.txt
```

### Testing
```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8

# Type checking
mypy src/

# Security scanning
bandit -r src/

# Dependency security check
safety check
```

### Database Management
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1

# Reset database (development only)
python scripts/init_db.py
```

### Development Server
```bash
# Run development server
python scripts/run_dev.py

# Or directly with uvicorn
uvicorn src.larp_manager_server.main:app --reload
```

## Architecture Overview

This is a FastAPI-based LARP (Live Action Role Playing) management system with the following key architectural patterns:

### Layered Architecture
- **API Layer**: FastAPI endpoints in `src/larp_manager_server/api/`
- **Service Layer**: Business logic in `src/larp_manager_server/services/`
- **Repository Layer**: Data access in `src/larp_manager_server/repositories/`
- **Model Layer**: SQLAlchemy models in `src/larp_manager_server/models/`
- **Schema Layer**: Pydantic schemas in `src/larp_manager_server/schemas/`

### Core Technologies
- **FastAPI**: Web framework with automatic OpenAPI documentation
- **SQLAlchemy 2.0**: Async ORM for PostgreSQL
- **Alembic**: Database migrations
- **Pydantic v2**: Data validation and serialization
- **AsyncPG**: PostgreSQL async driver
- **JWT**: Authentication via python-jose

### Key Domain Models
- **Users**: Authentication and base user management
- **Games**: LARP game instances with dates and descriptions
- **Players**: Links users to games with payment status
- **GMs**: Game masters assigned to games
- **Characters**: Player characters within games
- **Character Groups**: Groupings with min/max constraints
- **Plots**: Story elements involving characters/groups

### Database Features
- UUID primary keys for all entities
- PostgreSQL array fields for relationship management
- JSONB fields for flexible additional data
- Many-to-many associations between plots/characters/groups

## Development Guidelines

### Code Organization
- Follow the layered architecture pattern
- Use dependency injection for database sessions and authentication
- Implement proper error handling at service layer
- Use Pydantic schemas for all API input/output validation
- Follow async/await patterns throughout

### Testing Strategy
- Unit tests for services and repositories
- Integration tests for API endpoints
- Use pytest fixtures for test data
- Mock external dependencies
- Maintain >90% test coverage

### Authentication & Security
- JWT-based authentication with refresh tokens
- Role-based access control (User, Player, GM)
- Password hashing with bcrypt
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy

### Database Best Practices
- Use async database operations throughout
- Implement proper database connection pooling
- Use eager loading to prevent N+1 queries
- Index frequently queried fields
- Use transactions for multi-table operations

## Implementation Plan

The project follows a 5-phase implementation plan:

1. **Phase 1**: Foundation & Infrastructure (database, FastAPI setup)
2. **Phase 2**: Authentication System (JWT, user management)
3. **Phase 3**: Core Game Entities (games, players, GMs)
4. **Phase 4**: Characters, Plots & Advanced Features
5. **Phase 5**: Testing, Polish & Deployment

Each phase builds on the previous one with working, testable functionality.

## Important Notes

- The project uses Python 3.13+ with modern async patterns
- All database operations should be async
- Use proper type hints throughout (enforced by mypy)
- Follow PEP 8 style guidelines (enforced by black/flake8)
- Maintain comprehensive API documentation via FastAPI's auto-generation
- Use proper HTTP status codes and error responses
- Implement pagination for list endpoints
- Use environment variables for configuration