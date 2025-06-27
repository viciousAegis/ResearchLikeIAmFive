# ResearchLikeIAmFive Backend - Modular Architecture

This backend has been refactored into a modular, maintainable structure with separate concerns for better code organization.

## File Structure

```
backend/
├── __init__.py              # Package initialization
├── main.py                  # Main FastAPI application entry point
├── config.py                # Configuration and environment setup
├── security.py              # Security module (existing)
├── middleware.py            # FastAPI middleware configuration
├── routes.py                # API route handlers
├── ai_prompts.py           # AI prompt templates and schemas
├── ai_service.py           # Gemini AI service integration
├── arxiv_service.py        # ArXiv paper fetching logic
├── pdf_processor.py        # PDF processing and figure extraction
├── utils.py                # Shared utility functions
├── pyproject.toml          # Project dependencies
└── uv.lock                 # Lock file
```

## Module Responsibilities

### `main.py`
- **Purpose**: Main application entry point
- **Responsibilities**: 
  - FastAPI app initialization
  - Middleware configuration
  - Route registration
  - Application startup

### `config.py`
- **Purpose**: Configuration management
- **Responsibilities**:
  - Environment variable validation
  - Configuration constants
  - Gemini API client initialization
  - Logging setup

### `middleware.py`
- **Purpose**: FastAPI middleware setup
- **Responsibilities**:
  - Rate limiting configuration
  - CORS settings
  - Security headers
  - Request size limiting
  - Trusted host configuration

### `routes.py`
- **Purpose**: API endpoint definitions
- **Responsibilities**:
  - Route handlers
  - Request/response processing
  - Error handling
  - API documentation

### `ai_prompts.py`
- **Purpose**: AI prompt templates and schemas
- **Responsibilities**:
  - Style-specific prompt generation
  - JSON response schema definition
  - Prompt template management

### `ai_service.py`
- **Purpose**: AI service integration
- **Responsibilities**:
  - Gemini API communication
  - Response processing and validation
  - Error handling for AI service

### `arxiv_service.py`
- **Purpose**: ArXiv integration
- **Responsibilities**:
  - ArXiv ID extraction from URLs
  - Paper fetching from ArXiv
  - PDF downloading

### `pdf_processor.py`
- **Purpose**: PDF processing utilities
- **Responsibilities**:
  - Text extraction from PDFs
  - Figure extraction
  - File cleanup
  - Size validation

### `utils.py`
- **Purpose**: Shared utility functions
- **Responsibilities**:
  - JSON processing utilities
  - Text manipulation helpers
  - Common validation functions

### `security.py` (Existing)
- **Purpose**: Security features
- **Responsibilities**:
  - Input validation
  - Security headers
  - API key verification
  - Security event logging

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Testability**: Individual modules can be tested in isolation
4. **Reusability**: Utility functions can be shared across modules
5. **Scalability**: Easy to add new features without modifying existing code
6. **Readability**: Smaller, focused files are easier to understand

## Running the Application

The application can still be run the same way:

```bash
# Using uvicorn directly
uvicorn main:app --reload

# Or using the development server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Development Guidelines

1. **Keep modules focused**: Each module should have a single responsibility
2. **Use proper imports**: Import only what you need from other modules
3. **Add logging**: Use the configured logger for debugging and monitoring
4. **Handle errors**: Proper error handling and HTTP exceptions
5. **Document functions**: Add docstrings to all public functions
6. **Type hints**: Use type hints for better code clarity

## Adding New Features

1. **New AI styles**: Add to `ai_prompts.py`
2. **New endpoints**: Add to `routes.py`
3. **New processing logic**: Create new modules as needed
4. **New utilities**: Add to `utils.py` if shared, or create specific modules

This modular structure makes the codebase more professional, maintainable, and easier to work with as the project grows.
