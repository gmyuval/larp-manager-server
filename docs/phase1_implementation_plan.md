# Phase 1: Foundation & Infrastructure - Detailed Implementation Plan

## Overview

Phase 1 establishes the foundation for the LARP Manager Server, focusing on infrastructure, database connectivity, and core project structure. This phase creates the scaffolding that all subsequent phases will build upon.

## Pre-Implementation Setup

### Environment Verification
- Ensure Python 3.13+ is installed
- Verify PostgreSQL is available (local or Docker)
- Confirm all requirements from `requirements-dev.txt` are installable

### Project Structure Creation
Create the complete directory structure as defined in the design document:

```
src/larp_manager_server/
├── __init__.py
├── main.py
├── config.py
├── database.py
├── models/
│   ├── __init__.py
│   └── base.py
├── schemas/
│   └── __init__.py
├── services/
│   └── __init__.py
├── repositories/
│   └── __init__.py
├── api/
│   ├── __init__.py
│   └── dependencies.py
├── middleware/
│   └── __init__.py
└── utils/
    └── __init__.py
```

## Implementation Tasks

### Task 1: Environment Configuration System
**File**: `src/larp_manager_server/config.py`

**Implementation Details**:
- Use Pydantic Settings for configuration management
- Support both environment variables and .env file
- Include database configuration (URL, connection pooling settings)
- Add logging configuration
- Include basic security settings (secret key generation)

**Key Configuration Areas**:
- Database connection parameters
- Application settings (debug mode, API prefix)
- Security settings (JWT secret key placeholder)
- Logging configuration
- Development vs production mode settings

**Dependencies**: `pydantic-settings`, `python-dotenv`

### Task 2: Database Connection Setup
**File**: `src/larp_manager_server/database.py`

**Implementation Details**:
- Configure AsyncPG connection pool
- Set up SQLAlchemy 2.0 async engine
- Create database session management
- Implement connection lifecycle management
- Add health check functionality

**Key Components**:
- Async database engine creation
- Session factory for dependency injection
- Connection pool configuration
- Database health check function
- Schema namespace configuration (`larp_manager` schema)

**Dependencies**: `asyncpg`, `sqlalchemy[asyncio]`

### Task 3: Base Model Class
**File**: `src/larp_manager_server/models/base.py`

**Implementation Details**:
- Create SQLAlchemy declarative base class
- Define common fields for all models (id, created_at, updated_at)
- Implement UUID primary key generation
- Add common model methods (to_dict, etc.)
- Configure table naming convention

**Key Features**:
- UUID primary keys using `uuid.uuid4()`
- Timestamp fields with automatic update
- Common query methods
- Table name generation based on class name
- Schema assignment to `larp_manager`

**Database Schema Alignment**:
Based on the database structure, all tables should include:
- `id` (UUID, primary key)
- Standard timestamp fields for auditing
- Proper foreign key relationships
- Support for PostgreSQL-specific features (arrays, JSONB)

### Task 4: FastAPI Application Setup
**File**: `src/larp_manager_server/main.py`

**Implementation Details**:
- Create FastAPI application instance
- Configure CORS middleware
- Set up API documentation
- Implement application lifespan management
- Add basic health check endpoints

**Key Components**:
- Application factory pattern
- Middleware configuration
- Route organization with `/api/v1` prefix
- OpenAPI documentation setup
- Startup and shutdown event handlers

**Health Check Endpoints**:
- `GET /health` - Basic application health
- `GET /health/db` - Database connectivity check
- `GET /health/ready` - Readiness probe for deployment

### Task 5: Alembic Migration Configuration
**Files**: `alembic.ini`, `alembic/env.py`

**Implementation Details**:
- Configure Alembic for async SQLAlchemy
- Set up migration environment
- Configure schema targeting (`larp_manager`)
- Add migration template customization
- Implement auto-generation capabilities

**Key Configuration**:
- Async migration support
- Database URL from environment
- Schema-aware migrations
- Migration file naming convention
- Rollback support

### Task 6: Docker Compose Development Environment
**File**: `docker-compose.yml`

**Implementation Details**:
- PostgreSQL container configuration
- Database initialization with proper schema
- Volume mapping for persistence
- Environment variable configuration
- Development-friendly settings

**Container Configuration**:
- PostgreSQL 15+ with UUID extension
- Named volumes for data persistence
- Custom database initialization scripts
- Port mapping for local development
- Health check configuration

### Task 7: API Dependencies Setup
**File**: `src/larp_manager_server/api/dependencies.py`

**Implementation Details**:
- Database session dependency
- Basic request context setup
- Logging configuration
- Error handling helpers
- Dependency injection patterns

**Key Dependencies**:
- `get_db_session()` - Database session provider
- `get_current_context()` - Request context provider
- Basic security dependencies (placeholder for Phase 2)

### Task 8: Requirements Generation Script
**File**: `scripts/update_requirements.py`

**Implementation Details**:
- Automated requirements file generation using pip-compile
- Bidirectional constraint handling between requirements.txt and requirements-dev.txt
- Cross-platform compatibility (zsh/oh-my-zsh aware)
- Dependency resolution conflict handling
- Version pinning and security considerations

**Script Features**:
- Try dev-first approach: compile requirements-dev.txt, then use as constraint for requirements.txt
- Fallback to reverse approach if dev-first fails
- Automatic backup of existing requirements files
- Colored output for zsh terminal
- Progress indication and error reporting
- Integration with existing pip-tools workflow

**Dependencies**: `pip-tools`, `click` (for CLI interface)

**Script Implementation Strategy**:
```python
# Pseudocode for update_requirements.py
import subprocess
import shutil
import sys
from pathlib import Path

def update_requirements():
    """Update requirements files with bidirectional constraints."""
    
    # Strategy 1: Dev-first approach
    try:
        # Compile requirements-dev.txt first
        run_pip_compile("--extra=dev", "requirements-dev.txt")
        
        # Use dev as constraint for main requirements
        run_pip_compile(
            "--constraint=requirements-dev.txt", 
            "--output-file=requirements.txt",
            "pyproject.toml"
        )
        
        print("✅ Dev-first approach successful")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Dev-first approach failed: {e}")
        
        # Strategy 2: Reverse approach
        try:
            # Compile main requirements first
            run_pip_compile("--output-file=requirements.txt", "pyproject.toml")
            
            # Use main as constraint for dev requirements
            run_pip_compile(
                "--constraint=requirements.txt",
                "--extra=dev",
                "--output-file=requirements-dev.txt",
                "pyproject.toml"
            )
            
            print("✅ Reverse approach successful")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Both approaches failed: {e}")
            return False

def run_pip_compile(*args):
    """Run pip-compile with zsh-compatible output."""
    cmd = ["pip-compile", "--resolver=backtracking", "--upgrade"] + list(args)
    
    # Use zsh-compatible subprocess execution
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=False,  # Avoid shell=True for security
        env=os.environ.copy()
    )
    
    if result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"Error: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    
    return result
```

**Zsh Integration Features**:
- Colored output using ANSI escape codes
- Progress indicators with emoji (✅, ⚠️, ❌)
- Proper signal handling for Ctrl+C
- Environment variable preservation
- Compatible with oh-my-zsh plugins

### Task 9: Development Scripts
**File**: `scripts/init_db.py`

**Implementation Details**:
- Database initialization script
- Schema creation automation
- Development data setup
- Migration application
- Database reset functionality

**Script Features**:
- Async database operations
- Error handling and validation
- Environment-specific behavior
- Logging and progress indication
- Safe reset mechanisms
- Zsh-compatible output formatting

### Task 10: Dockerfile Creation
**File**: `Dockerfile`

**Implementation Details**:
- Multi-stage Docker build for production optimization
- Python 3.13+ base image with security updates
- Proper dependency installation and caching
- Non-root user setup for security
- Health check integration
- Production-ready configuration

**Dockerfile Features**:
- Multi-stage build (build stage + runtime stage)
- Efficient layer caching for dependencies
- Security best practices (non-root user, minimal attack surface)
- Health check endpoint integration
- Environment variable configuration
- Optimized for container orchestration

**Additional Files**:
- `.dockerignore` - Exclude unnecessary files from build context
- `docker-compose.prod.yml` - Production-like local testing environment

**Dockerfile Implementation Strategy**:
```dockerfile
# Multi-stage Dockerfile for LARP Manager Server

# Build stage
FROM python:3.13-slim as builder

# Set build arguments
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.13-slim as runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r larp \
    && useradd -r -g larp -d /app -s /bin/bash larp

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=larp:larp src/ ./src/
COPY --chown=larp:larp alembic/ ./alembic/
COPY --chown=larp:larp alembic.ini ./
COPY --chown=larp:larp scripts/ ./scripts/

# Switch to non-root user
USER larp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "src.larp_manager_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.dockerignore Implementation**:
```
# Git and version control
.git
.gitignore
.gitattributes

# Python cache and virtual environments
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
.env.*
!.env.example

# Development and testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
.mypy_cache/
.dmypy.json
dmypy.json

# IDE and editors
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Documentation and development files
docs/
README.md
*.md
!production.md

# Development tools
docker-compose.yml
docker-compose.*.yml
!docker-compose.prod.yml

# Build artifacts
build/
dist/
*.egg-info/
```

### Task 11: Environment Template
**File**: `.env.example`

**Implementation Details**:
- Complete environment variable documentation
- Development and production examples
- Security considerations
- Database configuration examples
- Feature flag examples

**Key Variables**:
```
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost/larp_manager_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0

# Application Settings
DEBUG=true
API_V1_PREFIX=/api/v1
PROJECT_NAME=LARP Manager Server

# Security (placeholder for Phase 2)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Database Schema Implementation

### Schema Creation Strategy
Based on the database structure document, Phase 1 will prepare for but not fully implement all tables. The focus is on infrastructure that supports the complete schema.

### Tables to Prepare Models For
While Phase 1 focuses on infrastructure, the base model should support the following table characteristics:

1. **UUID Primary Keys**: All tables use UUID primary keys
2. **Schema Namespace**: All tables belong to `larp_manager` schema
3. **Array Field Support**: PostgreSQL array columns (uuid[])
4. **JSONB Support**: Flexible additional data storage
5. **Proper Indexing**: Support for btree indexes on key fields

### Migration Strategy
- Initial migration creates the `larp_manager` schema
- Base tables structure prepared but not created
- Extension installation (uuid-ossp, etc.)
- Index creation templates

## Testing Strategy for Phase 1

### Unit Tests
- Configuration loading and validation
- Database connection and session management
- Base model functionality
- Health check endpoints

### Integration Tests
- Full application startup
- Database connectivity
- Migration application
- Docker environment setup

### Test Files to Create
- `tests/conftest.py` - Test configuration and fixtures
- `tests/test_config.py` - Configuration testing
- `tests/test_database.py` - Database connectivity testing
- `tests/test_health.py` - Health check endpoint testing

## Success Criteria

### Functional Requirements
1. **Application Startup**: FastAPI server starts without errors
2. **Database Connection**: Successfully connects to PostgreSQL
3. **Health Checks**: All health endpoints return 200 status
4. **Migration Support**: Alembic can create and apply migrations
5. **Development Environment**: Docker Compose environment works

### Technical Requirements
1. **Code Quality**: All code passes linting (black, flake8, mypy)
2. **Test Coverage**: >90% coverage for implemented components
3. **Documentation**: All modules have proper docstrings
4. **Configuration**: Environment-based configuration works
5. **Security**: Basic security practices implemented

### Performance Requirements
1. **Startup Time**: Application starts within 5 seconds
2. **Database Connection**: Connection pool initializes within 2 seconds
3. **Health Checks**: Health endpoints respond within 100ms
4. **Memory Usage**: Base application uses <50MB RAM

## Risk Mitigation

### Technical Risks
- **Database Connection Issues**: Implement retry logic and connection validation
- **Migration Conflicts**: Use proper migration naming and review process
- **Configuration Errors**: Validate all configuration on startup
- **Docker Issues**: Provide alternative local PostgreSQL setup

### Development Risks
- **Dependency Conflicts**: Pin all dependency versions
- **Environment Inconsistency**: Standardize development environment
- **Missing Dependencies**: Verify all requirements are installable

## Next Phase Preparation

### Phase 2 Readiness
- Authentication dependencies installed
- JWT configuration placeholder ready
- User model preparation (not implementation)
- Security middleware foundation

### Documentation Updates
- Update CLAUDE.md with Phase 1 learnings
- Document any architectural decisions
- Update README with setup instructions
- Create development guide

## Implementation Timeline

### Days 1-2: Core Infrastructure
- Environment configuration
- Database connection setup
- Base model class
- Project structure creation

### Days 3-4: Application Framework
- FastAPI application setup
- Health check endpoints
- Basic middleware configuration
- API dependencies

### Days 5-6: Development Environment & Containerization
- Docker Compose setup
- Alembic configuration
- Requirements generation script
- Dockerfile creation
- Development scripts

### Days 7-8: Testing, Validation & Documentation
- Comprehensive testing
- Container testing and validation
- Documentation completion
- Environment validation
- Phase 2 preparation

## Quality Assurance

### Code Review Checklist
- [ ] All code follows PEP 8 style guidelines
- [ ] Type hints are complete and accurate
- [ ] Docstrings are comprehensive
- [ ] Error handling is appropriate
- [ ] Configuration is environment-agnostic
- [ ] Security best practices are followed
- [ ] Tests cover all functionality
- [ ] Documentation is complete

### Testing Checklist
- [ ] Unit tests pass with >90% coverage
- [ ] Integration tests validate full stack
- [ ] Docker environment works correctly
- [ ] Health checks respond properly
- [ ] Database connectivity is stable
- [ ] Migration system works
- [ ] Configuration validation works
- [ ] Error handling is appropriate

This detailed implementation plan provides a comprehensive roadmap for Phase 1, ensuring all infrastructure components are properly established before moving to Phase 2's authentication system.