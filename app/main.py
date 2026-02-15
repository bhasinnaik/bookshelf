from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
from datetime import datetime
import os
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.models import (
    Book, BookCreate, BookUpdate, Bookshelf,
    BookDB, BookshelfDB,
    Review, ReviewCreate, ReviewDB
)

# Create all tables (including reviews)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bookshelf API",
    description="A comprehensive API for managing a bookshelf",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Initialize Sample Data ====================

def init_sample_data(db: Session):
    """Initialize database with sample data if empty."""
    if db.query(BookDB).first() is None:
        # Add sample books
        books = [
            BookDB(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                isbn="9780743273565",
                publication_year=1925,
                pages=180,
                genre="Fiction",
                description="A classic American novel set in the Jazz Age."
            ),
            BookDB(
                title="To Kill a Mockingbird",
                author="Harper Lee",
                isbn="9780061120084",
                publication_year=1960,
                pages=281,
                genre="Fiction",
                description="A gripping tale of racial injustice in the American South."
            ),
        ]
        
        for book in books:
            db.add(book)
        db.commit()
        
        # Add sample bookshelf
        shelf = BookshelfDB(
            name="My Reading Collection",
            owner="John Doe"
        )
        shelf.books = books
        db.add(shelf)
        db.commit()

# Initialize data on startup
db_session = next(get_db())
init_sample_data(db_session)

# ==================== Root Endpoints ====================
# Note: Root endpoint will be replaced with static file serving below

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Bookshelf API"}


# ==================== Book Endpoints ====================

@app.get("/books", response_model=List[Book])
async def list_books(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    author: Optional[str] = Query(None, description="Filter by author"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all books with optional filtering."""
    query = db.query(BookDB)
    
    if genre:
        query = query.filter(BookDB.genre.ilike(f"%{genre}%"))
    if author:
        query = query.filter(BookDB.author.ilike(f"%{author}%"))
    
    books = query.offset(skip).limit(limit).all()
    return books

@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by ID, including reviews."""
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book

# ==================== Review Endpoints ====================

@app.post("/books/{book_id}/reviews", response_model=Review, status_code=201)
async def create_review(book_id: int, review: ReviewCreate, db: Session = Depends(get_db)):
    """Create a review for a book."""
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    review_db = ReviewDB(**review.dict(), book_id=book_id)
    db.add(review_db)
    db.commit()
    db.refresh(review_db)
    return review_db

@app.get("/books/{book_id}/reviews", response_model=List[Review])
async def list_reviews(book_id: int, db: Session = Depends(get_db)):
    """List all reviews for a book."""
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book.reviews

@app.delete("/books/{book_id}/reviews/{review_id}")
async def delete_review(book_id: int, review_id: int, db: Session = Depends(get_db)):
    """Delete a review for a book."""
    review = db.query(ReviewDB).filter(ReviewDB.id == review_id, ReviewDB.book_id == book_id).first()
    if not review:
        raise HTTPException(status_code=404, detail=f"Review with id {review_id} not found for book {book_id}")
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully", "review_id": review_id}

@app.post("/books", response_model=Book, status_code=201)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Create a new book."""
    # Check for duplicate ISBN
    existing_book = db.query(BookDB).filter(BookDB.isbn == book.isbn).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    
    new_book = BookDB(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book

@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    """Update a book."""
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    
    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    book.updated_at = datetime.utcnow()
    db.add(book)
    db.commit()
    db.refresh(book)
    
    return book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book."""
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    
    db.delete(book)
    db.commit()
    
    return {"message": "Book deleted successfully", "book_id": book_id}

# ==================== Bookshelf Endpoints ====================

@app.get("/bookshelves", response_model=List[Bookshelf])
async def list_bookshelves(db: Session = Depends(get_db)):
    """Get all bookshelves."""
    shelves = db.query(BookshelfDB).all()
    return shelves

@app.get("/bookshelves/{bookshelf_id}", response_model=Bookshelf)
async def get_bookshelf(bookshelf_id: int, db: Session = Depends(get_db)):
    """Get a specific bookshelf."""
    shelf = db.query(BookshelfDB).filter(BookshelfDB.id == bookshelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail=f"Bookshelf with id {bookshelf_id} not found")
    
    return shelf

@app.post("/bookshelves", status_code=201)
async def create_bookshelf(name: str, owner: str, db: Session = Depends(get_db)):
    """Create a new bookshelf."""
    new_shelf = BookshelfDB(name=name, owner=owner)
    db.add(new_shelf)
    db.commit()
    db.refresh(new_shelf)
    
    return {"message": "Bookshelf created", "bookshelf": new_shelf}

@app.post("/bookshelves/{bookshelf_id}/books/{book_id}")
async def add_book_to_bookshelf(bookshelf_id: int, book_id: int, db: Session = Depends(get_db)):
    """Add a book to a bookshelf."""
    shelf = db.query(BookshelfDB).filter(BookshelfDB.id == bookshelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail=f"Bookshelf with id {bookshelf_id} not found")
    
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    
    if book in shelf.books:
        raise HTTPException(status_code=400, detail="Book already in this bookshelf")
    
    shelf.books.append(book)
    db.add(shelf)
    db.commit()
    
    return {"message": "Book added to bookshelf"}

@app.delete("/bookshelves/{bookshelf_id}/books/{book_id}")
async def remove_book_from_bookshelf(bookshelf_id: int, book_id: int, db: Session = Depends(get_db)):
    """Remove a book from a bookshelf."""
    shelf = db.query(BookshelfDB).filter(BookshelfDB.id == bookshelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail=f"Bookshelf with id {bookshelf_id} not found")
    
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if book not in shelf.books:
        raise HTTPException(status_code=404, detail="Book not in this bookshelf")
    
    shelf.books.remove(book)
    db.add(shelf)
    db.commit()
    
    return {"message": "Book removed from bookshelf"}

@app.get("/bookshelves/{bookshelf_id}/stats")
async def get_bookshelf_stats(bookshelf_id: int, db: Session = Depends(get_db)):
    """Get statistics for a bookshelf."""
    shelf = db.query(BookshelfDB).filter(BookshelfDB.id == bookshelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail=f"Bookshelf with id {bookshelf_id} not found")
    
    shelf_books = shelf.books
    
    if not shelf_books:
        return {
            "bookshelf_id": bookshelf_id,
            "total_books": 0,
            "total_pages": 0,
            "avg_pages": 0,
            "genres": []
        }
    
    genres = {}
    for book in shelf_books:
        genre = book.genre
        genres[genre] = genres.get(genre, 0) + 1
    
    total_pages = sum(b.pages for b in shelf_books)
    
    return {
        "bookshelf_id": bookshelf_id,
        "bookshelf_name": shelf.name,
        "total_books": len(shelf_books),
        "total_pages": total_pages,
        "avg_pages": round(total_pages / len(shelf_books), 2),
        "genres": genres
    }

# ==================== Static Files ====================

from fastapi.responses import FileResponse

# Mount static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Serve index.html for root path
@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the frontend website."""
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return FileResponse(os.path.join(static_path, 'index.html'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
