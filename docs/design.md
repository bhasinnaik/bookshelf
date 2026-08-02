# Bookshelf API Design Documentation

## Overview

The Bookshelf API is a small FastAPI application for managing books, bookshelves, and book reviews. It combines a REST API backend with a static frontend that runs in the browser and interacts with the API.

## Project Structure

- `app/`
  - `main.py` - FastAPI application and API endpoint definitions.
  - `models.py` - SQLAlchemy ORM models and Pydantic schemas.
  - `database.py` - Database engine and session management.
  - `config.py` - Application settings and environment configuration.
- `static/`
  - `index.html` - Single-page frontend for interacting with the app.
  - `css/style.css` - Frontend styling.
  - `js/api.js` - API helper functions for browser requests.
  - `js/app.js` - Frontend UI and event logic.
- `requirements.txt` - Python dependencies.
- `tests/` - Test suite for the application.

## Architecture

The application follows a simple web architecture:

1. **Frontend**
   - Served as static files by FastAPI.
   - Uses vanilla JavaScript to call REST endpoints and render the UI.
   - Includes book listing, filtering, book detail modal, bookshelf management, and review creation.

2. **Backend**
   - FastAPI handles HTTP requests and returns JSON.
   - SQLAlchemy maps Python objects to the SQLite database.
   - Pydantic validates request and response data.

3. **Database**
   - SQLite is used as the local persistence engine.
   - Schemas are created automatically at startup via `Base.metadata.create_all(bind=engine)`.

## Data Models

### Book

- Fields:
  - `id`: integer primary key
  - `title`: string
  - `author`: string
  - `isbn`: string
  - `publication_year`: integer
  - `pages`: integer
  - `genre`: string
  - `description`: optional string
  - `created_at`: datetime
  - `updated_at`: datetime
- Relationships:
  - `bookshelves`: many-to-many via `bookshelf_books` association table
  - `reviews`: one-to-many with `ReviewDB`

### Review

- Fields:
  - `id`: primary key
  - `book_id`: foreign key to `books.id`
  - `reviewer`: string
  - `rating`: float (0 to 5)
  - `comment`: optional string
  - `created_at`: datetime
- Relationship:
  - `book`: parent `BookDB`

### Bookshelf

- Fields:
  - `id`: primary key
  - `name`: string
  - `owner`: string
  - `created_at`: datetime
- Relationship:
  - `books`: many-to-many with `BookDB`

## API Endpoints

### Health

- `GET /health`
  - Returns service health status.

### Books

- `GET /books`
  - List books with optional `author`, `genre`, `skip`, and `limit` filters.

- `GET /books/{book_id}`
  - Retrieve a single book, including its reviews.

- `POST /books`
  - Create a new book record.

- `PUT /books/{book_id}`
  - Update an existing book.

- `DELETE /books/{book_id}`
  - Delete a book.

### Reviews

- `POST /books/{book_id}/reviews`
  - Add a review for a book.

- `GET /books/{book_id}/reviews`
  - List reviews for a book.

- `DELETE /books/{book_id}/reviews/{review_id}`
  - Delete a book review.

### Bookshelves

- `GET /bookshelves`
  - List all bookshelves.

- `GET /bookshelves/{bookshelf_id}`
  - Get bookshelf details.

- `POST /bookshelves`
  - Create a bookshelf.

- `POST /bookshelves/{bookshelf_id}/books/{book_id}`
  - Add a book to a bookshelf.

- `DELETE /bookshelves/{bookshelf_id}/books/{book_id}`
  - Remove a book from a bookshelf.

- `GET /bookshelves/{bookshelf_id}/stats`
  - Get bookshelf statistics.

## Frontend Interaction

### Main UI

- Book listing and filtering
- Add a book form
- Bookshelf list and creation
- Book details modal

### Review UI

- The book detail modal shows reviews for the selected book.
- Users can add a review with:
  - reviewer name
  - rating
  - optional comment
- Reviews can also be deleted from the modal.

### Client API Layer

- `static/js/api.js` encapsulates fetch operations.
- The frontend uses `api.books` and `api.reviews` methods to interact with the backend.

## Deployment

### Local development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

### Docker Compose

```bash
docker-compose up --build
```

## Notes

- The database is SQLite and is created in the repository root.
- Static frontend files are mounted and served by FastAPI.
- The app supports CORS for browser usage.
- The design is intentionally simple and extensible for future auth, pagination, or analytics.
