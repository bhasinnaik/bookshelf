from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# ==================== SQLAlchemy ORM Models ====================

# Association table for many-to-many relationship
bookshelf_books = Table(
    'bookshelf_books',
    Base.metadata,
    Column('bookshelf_id', Integer, ForeignKey('bookshelves.id'), primary_key=True),
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True)
)

class BookDB(Base):
    """SQLAlchemy model for Book."""
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    author = Column(String(255), index=True)
    isbn = Column(String(13), unique=True, index=True)
    publication_year = Column(Integer)
    pages = Column(Integer)
    genre = Column(String(100), index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    bookshelves = relationship(
        "BookshelfDB",
        secondary=bookshelf_books,
        back_populates="books"
    )
    # Reviews relationship
    reviews = relationship("ReviewDB", back_populates="book", cascade="all, delete-orphan")


# ==================== Review Model ====================
from sqlalchemy import Float

class ReviewDB(Base):
    """SQLAlchemy model for Book Review."""
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    reviewer = Column(String(100), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    book = relationship("BookDB", back_populates="reviews")

class BookshelfDB(Base):
    """SQLAlchemy model for Bookshelf."""
    __tablename__ = "bookshelves"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    owner = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    books = relationship(
        "BookDB",
        secondary=bookshelf_books,
        back_populates="bookshelves"
    )

# ==================== Pydantic Models ====================

class ItemBase(BaseModel):
    """Base item model."""
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    """Item creation model."""
    pass

class ItemUpdate(BaseModel):
    """Item update model."""
    name: Optional[str] = None
    description: Optional[str] = None

class Item(ItemBase):
    """Item response model."""
    id: int
    
    class Config:
        from_attributes = True

# ==================== Review Pydantic Models ====================

class ReviewBase(BaseModel):
    reviewer: str
    rating: float = Field(..., ge=0, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class Book(BaseModel):
    """Book model with ID and metadata."""
    id: int
    title: str
    author: str
    isbn: str
    publication_year: int
    pages: int
    genre: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reviews: List[Review] = []
    class Config:
        from_attributes = True

class BookBase(BaseModel):
    """Base model for book data."""
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=10, max_length=13)
    publication_year: int
    pages: int = Field(..., gt=0)
    genre: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class BookCreate(BookBase):
    """Model for creating a new book."""
    pass

class BookUpdate(BaseModel):
    """Model for updating a book."""
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    pages: Optional[int] = None
    genre: Optional[str] = None
    description: Optional[str] = None

class Book(BookBase):
    """Book model with ID and metadata."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Bookshelf(BaseModel):
    """Bookshelf model."""
    id: int
    name: str
    owner: str
    books: List[Book] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

