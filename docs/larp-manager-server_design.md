# LARP Manager Server - Design Document

## Project Overview

The LARP Manager Server is a backend system designed to manage Live Action Role Playing (LARP) games. This system provides comprehensive management capabilities for users, games, characters, character groups, plots, and game masters through a RESTful API architecture.

### Key Features
- User management with authentication and authorization
- Game creation and management
- Character and character group management
- Plot management with character/group associations
- Player and Game Master role management
- Combined endpoints for complex data retrieval
- Role-based access control

### Technology Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT with python-jose
- **Password Hashing**: Passlib with bcrypt
- **Python Version**: >=3.13.5

## Architecture Overview

The system follows a layered architecture pattern with clear separation of concerns:

1. **API Layer** - FastAPI endpoints for HTTP request handling
2. **Service Layer** - Business logic and transaction management
3. **Repository Layer** - Data access and database operations
4. **Model Layer** - SQLAlchemy ORM models and database schema
5. **Schema Layer** - Pydantic models for request/response validation

## Project Structure

```
larp-manager-server/                    # Root directory
├── pyproject.toml                      # Project configuration
├── README.md                           # Project documentation
├── LICENSE                             # License file
├── requirements.txt                    # Production dependencies
├── requirements-dev.txt               # Development dependencies
├── environment.yml                     # Conda environment
├── .gitignore                         # Git ignore rules
├── .env                               # Environment variables
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Development PostgreSQL setup
├── src/                               # Source code directory
│   └── larp_manager_server/           # Main package
│       ├── __init__.py
│       ├── main.py                    # FastAPI application entry point
│       ├── config.py                  # Configuration management
│       ├── database.py                # Database connection setup
│       ├── models/                    # SQLAlchemy ORM models
│       │   ├── __init__.py
│       │   ├── base.py               # Base model class
│       │   ├── user.py               # User model
│       │   ├── game.py               # Game model
│       │   ├── character.py          # Character model
│       │   ├── player.py             # Player model
│       │   ├── gm.py                 # GM model
│       │   ├── plot.py               # Plot model
│       │   ├── character_group.py    # Character Group model
│       │   └── associations.py       # Many-to-many association tables
│       ├── schemas/                   # Pydantic validation schemas
│       │   ├── __init__.py
│       │   ├── user.py               # User schemas
│       │   ├── game.py               # Game schemas
│       │   ├── character.py          # Character schemas
│       │   ├── player.py             # Player schemas
│       │   ├── gm.py                 # GM schemas
│       │   ├── plot.py               # Plot schemas
│       │   ├── character_group.py    # Character Group schemas
│       │   └── auth.py               # Authentication schemas
│       ├── services/                  # Business logic layer
│       │   ├── __init__.py
│       │   ├── auth_service.py       # Authentication business logic
│       │   ├── user_service.py       # User management
│       │   ├── game_service.py       # Game management
│       │   ├── character_service.py  # Character management
│       │   ├── player_service.py     # Player management
│       │   ├── gm_service.py         # GM management
│       │   └── plot_service.py       # Plot management
│       ├── repositories/              # Data access layer
│       │   ├── __init__.py
│       │   ├── base_repository.py    # Generic CRUD operations
│       │   ├── user_repository.py    # User data access
│       │   ├── game_repository.py    # Game data access
│       │   ├── character_repository.py # Character data access
│       │   ├── player_repository.py  # Player data access
│       │   ├── gm_repository.py      # GM data access
│       │   └── plot_repository.py    # Plot data access
│       ├── api/                       # FastAPI route definitions
│       │   ├── __init__.py
│       │   ├── dependencies.py       # Common dependencies
│       │   ├── auth.py              # Authentication endpoints
│       │   ├── users.py             # User CRUD endpoints
│       │   ├── games.py             # Game CRUD endpoints
│       │   ├── characters.py        # Character CRUD endpoints
│       │   ├── players.py           # Player CRUD endpoints
│       │   ├── gms.py               # GM CRUD endpoints
│       │   ├── plots.py             # Plot CRUD endpoints
│       │   ├── character_groups.py  # Character Group CRUD endpoints
│       │   └── combined.py          # Combined/complex endpoints
│       ├── middleware/                # Custom middleware
│       │   ├── __init__.py
│       │   ├── auth_middleware.py   # Authentication middleware
│       │   ├── cors_middleware.py   # CORS handling
│       │   └── error_handler.py     # Global error handling
│       └── utils/                     # Utility functions
│           ├── __init__.py
│           ├── security.py          # Security utilities
│           ├── helpers.py           # General helpers
│           └── pagination.py        # Pagination utilities
├── alembic/                           # Database migrations
│   ├── env.py                        # Alembic environment
│   ├── script.py.mako               # Migration template
│   └── versions/                     # Migration files
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Test configuration
│   ├── test_auth.py                  # Authentication tests
│   ├── test_users.py                 # User endpoint tests
│   ├── test_games.py                 # Game endpoint tests
│   ├── test_characters.py           # Character endpoint tests
│   └── test_combined.py             # Combined endpoint tests
├── scripts/                           # Utility scripts
│   ├── init_db.py                    # Database initialization
│   ├── create_admin.py               # Create admin user
│   ├── seed_data.py                  # Seed sample data
│   └── run_dev.py                    # Development server runner
└── docs/                             # Documentation
    ├── larp_manager_db_structure.md  # Database structure
    ├── larp_manager_db_graph.png     # Database diagram
    ├── larp_manager_db_model.dbm     # Database model
    ├── larp-manager-server_design.md # This design document
    └── api/                          # API documentation
        ├── endpoints.md              # Endpoint documentation
        └── examples.md               # API usage examples
```

## Database Analysis

### Core Tables
- **users** - Base authentication entity with email, password, name, phone
- **games** - Game management with dates, descriptions, and additional schema support
- **players** - Links users to games with payment status and additional details
- **gms** - Links users to games as game masters
- **characters** - Player characters within games
- **character_groups** - Groupings of characters with min/max constraints
- **plots** - Story elements that can involve characters and character groups

### Relationships
- **Many-to-many associations** between plots, characters, and character groups
- **Foreign key relationships** linking users to players/GMs and games
- **Array fields** for denormalized access patterns (character_ids, plot_ids)
- **JSONB fields** for flexible additional data storage

### Key Features
- **UUID primary keys** for all entities
- **PostgreSQL array support** for relationship management
- **JSONB support** for flexible schema extensions
- **Proper indexing** on frequently queried fields

## Core Components

### Model Layer
- **Base Model Class** - Common fields and methods for all entities
- **SQLAlchemy 2.0 Models** - Async-compatible ORM models
- **Relationship Management** - Proper foreign keys and associations
- **UUID Support** - Primary keys matching database schema
- **Array Field Support** - PostgreSQL array column handling

### Schema Layer
- **Pydantic v2 Models** - Request/response validation
- **Separate Schema Types** - Create, Update, Response schemas
- **Custom Validators** - Business rule validation
- **Nested Schemas** - Complex object validation
- **Email Validation** - Built-in email format validation

### Repository Layer
- **Base Repository** - Generic CRUD operations
- **Entity-Specific Repositories** - Specialized query methods
- **Async Database Operations** - Non-blocking database calls
- **Query Optimization** - Efficient data retrieval patterns
- **Transaction Support** - Proper database transaction handling

### Service Layer
- **Business Logic** - Domain-specific operations
- **Transaction Management** - Multi-table operations
- **Data Transformation** - Format conversion and validation
- **Complex Operations** - User registration, role assignment
- **Error Handling** - Business rule validation and error response

### API Layer
- **FastAPI Routers** - Organized endpoint grouping
- **Dependency Injection** - Authentication and database session management
- **Request Validation** - Automatic request body validation
- **Response Serialization** - Automatic response formatting
- **Error Handling** - HTTP status code mapping

## FastAPI Implementation

### Main Application Structure
The FastAPI application is organized with:
- **Application Factory** - Centralized app configuration
- **Middleware Stack** - CORS, authentication, error handling
- **Router Organization** - Logical endpoint grouping
- **Lifespan Management** - Startup and shutdown procedures
- **Auto-Documentation** - OpenAPI/Swagger integration

### Endpoint Organization
- **Version Prefixing** - `/api/v1/` for all endpoints
- **Resource Grouping** - Logical endpoint organization
- **Standard HTTP Methods** - RESTful operation mapping
- **Consistent Response Format** - Uniform API responses
- **Comprehensive Documentation** - Auto-generated API docs

## Authentication System

### JWT-Based Authentication
- **Access Tokens** - Short-lived authentication tokens
- **Refresh Tokens** - Long-lived token renewal mechanism
- **Token Validation** - Middleware-based token verification
- **Password Security** - bcrypt hashing with salt rounds
- **Role-Based Access** - User, Player, GM role management

### Security Features
- **Password Complexity** - Enforced password requirements
- **Token Expiration** - Configurable token lifetimes
- **Secure Headers** - CORS and security middleware
- **Rate Limiting** - API request throttling
- **Input Sanitization** - SQL injection prevention

## API Endpoints

### Authentication Endpoints (`/api/v1/auth`)
- **POST /register** - User registration
- **POST /login** - User authentication
- **POST /refresh** - Token renewal
- **POST /logout** - User logout
- **GET /me** - Current user information

### Standard CRUD Endpoints
Each entity (users, games, characters, players, gms, plots, character-groups) provides:
- **GET /** - List resources (with pagination)
- **POST /** - Create new resource
- **GET /{id}** - Retrieve specific resource
- **PUT /{id}** - Update existing resource
- **DELETE /{id}** - Delete resource

### Combined/Complex Endpoints (`/api/v1/combined`)
- **Player with User Details** - Enhanced player information
- **Character with Relations** - Character with player and user data
- **Game with Full Details** - Complete game information
- **Plot with Participants** - Plot with associated characters and groups
- **GM with Game Details** - Game master information with managed games

### Query Parameters
- **Pagination** - `page`, `size` parameters
- **Filtering** - Entity-specific filter parameters
- **Sorting** - `sort_by`, `sort_order` parameters
- **Field Selection** - `fields` parameter for partial responses
- **Search** - `search` parameter for text-based queries

## Development Tools

### Database Management
- **Alembic Migrations** - Schema version control
- **Database Initialization** - Automated schema setup
- **Seed Data Scripts** - Sample data population
- **Admin User Creation** - Initial user setup

### Development Scripts
- **Development Server** - Auto-reloading development server
- **Database Reset** - Clean database recreation
- **Test Data Generation** - Automated test data creation
- **Migration Management** - Database schema updates

### Testing Infrastructure
- **Pytest Configuration** - Test framework setup
- **Test Database** - Isolated test environment
- **Fixture Management** - Reusable test data
- **Coverage Reports** - Code coverage analysis

### Docker Support
- **Development Environment** - Local PostgreSQL setup
- **Container Configuration** - Multi-service orchestration
- **Environment Variables** - Configuration management
- **Volume Management** - Data persistence

## Technical Considerations

### Performance Optimization
- **Database Connection Pooling** - Efficient connection management
- **Query Optimization** - Efficient database queries
- **Eager Loading** - Reduced N+1 query problems
- **Caching Strategy** - Frequently accessed data caching
- **Pagination Implementation** - Large dataset handling

### Security Implementation
- **Input Validation** - Comprehensive data validation
- **SQL Injection Prevention** - Parameterized queries
- **XSS Protection** - Output encoding
- **CORS Configuration** - Cross-origin request handling
- **Error Information Leakage** - Sanitized error responses

### Scalability Planning
- **Async Architecture** - Non-blocking operations
- **Database Optimization** - Proper indexing and query patterns
- **API Rate Limiting** - Request throttling
- **Monitoring Integration** - Performance tracking
- **Horizontal Scaling** - Multi-instance deployment support

### Error Handling Strategy
- **Global Exception Handling** - Consistent error responses
- **HTTP Status Code Mapping** - Proper status code usage
- **Detailed Error Messages** - Development-friendly error information
- **Error Logging** - Comprehensive error tracking
- **Graceful Degradation** - Fallback mechanisms

### Configuration Management
- **Environment Variables** - External configuration
- **Settings Validation** - Configuration verification
- **Development/Production Modes** - Environment-specific settings
- **Secret Management** - Secure credential handling
- **Feature Flags** - Optional functionality toggling

## Future Considerations

### Potential Enhancements
- **Real-time Updates** - WebSocket integration
- **File Upload Support** - Character images and documents
- **Email Notifications** - User communication system
- **Advanced Search** - Full-text search capabilities
- **API Versioning** - Backward compatibility support

### Monitoring and Observability
- **Health Check Endpoints** - System status monitoring
- **Metrics Collection** - Performance metrics
- **Logging Framework** - Structured logging
- **Error Tracking** - Exception monitoring
- **Performance Profiling** - Bottleneck identification

This design document serves as the foundation for implementing the LARP Manager Server, providing a comprehensive overview of the system architecture, component organization, and technical implementation strategy.
