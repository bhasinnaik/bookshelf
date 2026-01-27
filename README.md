# FastAPI Application Template

A modern FastAPI project template with best practices for building RESTful APIs.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── config.py            # Configuration settings
│   └── models.py            # Pydantic models
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Sample tests
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

## Running the Application

### Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Running Tests

```bash
pytest tests/
```

Or with coverage:

```bash
pytest tests/ --cov=app
```

## API Endpoints

### Available Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /items/{item_id}` - Get item by ID
- `POST /items/` - Create new item

## Features

- ✅ FastAPI framework with async support
- ✅ Pydantic models for data validation
- ✅ CORS middleware configured
- ✅ Environment configuration
- ✅ Unit tests with pytest
- ✅ API documentation (Swagger & ReDoc)

## Development

### Code Style

Consider using:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

```bash
pip install black flake8 mypy
```

### Useful Commands

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

## Production Deployment

For production, consider:

1. Using a production ASGI server (Gunicorn with Uvicorn workers)
2. Setting `debug=False` in settings
3. Using environment-specific configurations
4. Implementing proper error handling and logging
5. Adding authentication and authorization
6. Setting up HTTPS

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## License

MIT

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
