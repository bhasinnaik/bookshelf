// DOM Elements
const navButtons = document.querySelectorAll('.nav-btn');
const tabContents = document.querySelectorAll('.tab-content');
const booksList = document.getElementById('booksList');
const shelvesList = document.getElementById('shelvesList');
const addBookForm = document.getElementById('addBookForm');
const createShelfBtn = document.getElementById('createShelfBtn');
const filterBtn = document.getElementById('filterBtn');
const clearFilterBtn = document.getElementById('clearFilterBtn');
const bookModal = document.getElementById('bookModal');
const shelfModal = document.getElementById('shelfModal');
const modalClose = document.querySelectorAll('.close');

// Event Listeners
navButtons.forEach(btn => {
    btn.addEventListener('click', handleTabSwitch);
});

addBookForm.addEventListener('submit', handleAddBook);
createShelfBtn.addEventListener('click', handleCreateShelf);
filterBtn.addEventListener('click', handleFilterBooks);
clearFilterBtn.addEventListener('click', handleClearFilter);

modalClose.forEach(closeBtn => {
    closeBtn.addEventListener('click', (e) => {
        e.target.closest('.modal').style.display = 'none';
    });
});

window.addEventListener('click', (e) => {
    if (e.target === bookModal) bookModal.style.display = 'none';
    if (e.target === shelfModal) shelfModal.style.display = 'none';
});

// Tab Switching
function handleTabSwitch(e) {
    const tabName = e.target.dataset.tab;

    // Update active nav button
    navButtons.forEach(btn => btn.classList.remove('active'));
    e.target.classList.add('active');

    // Show active tab
    tabContents.forEach(content => content.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');

    // Load data for specific tabs
    if (tabName === 'books') {
        loadBooks();
    } else if (tabName === 'bookshelves') {
        loadBookshelves();
    }
}

// Load Books
async function loadBooks() {
    try {
        booksList.innerHTML = '<p class="loading">Loading books...</p>';
        const books = await api.books.list();
        
        if (books.length === 0) {
            booksList.innerHTML = '<p class="loading">No books found. Add one to get started!</p>';
            return;
        }

        booksList.innerHTML = books.map(book => `
            <div class="book-card" onclick="showBookDetails(${book.id})">
                <h3>${escapeHtml(book.title)}</h3>
                <p class="author">by ${escapeHtml(book.author)}</p>
                <div class="book-meta">
                    <div>📅 ${book.publication_year}</div>
                    <div>📖 ${book.pages} pages</div>
                    <div>ISBN: ${book.isbn}</div>
                </div>
                <span class="book-genre">${escapeHtml(book.genre)}</span>
                <div class="book-actions">
                    <button class="btn btn-secondary" onclick="event.stopPropagation(); deleteBook(${book.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        booksList.innerHTML = `<p class="loading">Error loading books: ${error.message}</p>`;
    }
}

// Load Bookshelves
async function loadBookshelves() {
    try {
        shelvesList.innerHTML = '<p class="loading">Loading bookshelves...</p>';
        const shelves = await api.shelves.list();
        
        if (shelves.length === 0) {
            shelvesList.innerHTML = '<p class="loading">No bookshelves yet. Create one!</p>';
            return;
        }

        shelvesList.innerHTML = shelves.map(shelf => `
            <div class="shelf-card">
                <h3>${escapeHtml(shelf.name)}</h3>
                <div class="shelf-info">👤 ${escapeHtml(shelf.owner)}</div>
                <span class="book-count">${shelf.books.length} books</span>
                <div class="shelf-actions-buttons">
                    <button class="btn btn-primary" onclick="showShelfDetails(${shelf.id})">View</button>
                    <button class="btn btn-secondary" onclick="showAddBookToShelf(${shelf.id})">Add Book</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        shelvesList.innerHTML = `<p class="loading">Error loading bookshelves: ${error.message}</p>`;
    }
}

// Add Book
async function handleAddBook(e) {
    e.preventDefault();

    const bookData = {
        title: document.getElementById('bookTitle').value,
        author: document.getElementById('bookAuthor').value,
        isbn: document.getElementById('bookISBN').value,
        publication_year: parseInt(document.getElementById('bookYear').value),
        pages: parseInt(document.getElementById('bookPages').value),
        genre: document.getElementById('bookGenre').value,
        description: document.getElementById('bookDescription').value || null,
    };

    try {
        await api.books.create(bookData);
        showAlert('Book added successfully!', 'success');
        addBookForm.reset();
        loadBooks();
    } catch (error) {
        showAlert(`Error adding book: ${error.message}`, 'error');
    }
}

// Delete Book
async function deleteBook(bookId) {
    if (!confirm('Are you sure you want to delete this book?')) return;

    try {
        await api.books.delete(bookId);
        showAlert('Book deleted successfully!', 'success');
        loadBooks();
    } catch (error) {
        showAlert(`Error deleting book: ${error.message}`, 'error');
    }
}

// Show Book Details
async function showBookDetails(bookId) {
    try {
        const book = await api.books.get(bookId);
        const modalBody = document.getElementById('modalBody');
        
        modalBody.innerHTML = `
            <h2>${escapeHtml(book.title)}</h2>
            <p><strong>Author:</strong> ${escapeHtml(book.author)}</p>
            <p><strong>ISBN:</strong> ${book.isbn}</p>
            <p><strong>Publication Year:</strong> ${book.publication_year}</p>
            <p><strong>Pages:</strong> ${book.pages}</p>
            <p><strong>Genre:</strong> <span class="book-genre">${escapeHtml(book.genre)}</span></p>
            ${book.description ? `<p><strong>Description:</strong> ${escapeHtml(book.description)}</p>` : ''}
            <p><strong>Added:</strong> ${new Date(book.created_at).toLocaleDateString()}</p>
        `;

        bookModal.style.display = 'block';
    } catch (error) {
        showAlert(`Error loading book details: ${error.message}`, 'error');
    }
}

// Create Shelf
async function handleCreateShelf() {
    const name = document.getElementById('shelfName').value.trim();
    const owner = document.getElementById('shelfOwner').value.trim();

    if (!name || !owner) {
        showAlert('Please enter both shelf name and owner', 'error');
        return;
    }

    try {
        await api.shelves.create(name, owner);
        showAlert('Bookshelf created successfully!', 'success');
        document.getElementById('shelfName').value = '';
        document.getElementById('shelfOwner').value = '';
        loadBookshelves();
    } catch (error) {
        showAlert(`Error creating shelf: ${error.message}`, 'error');
    }
}

// Show Shelf Details
async function showShelfDetails(shelfId) {
    try {
        const shelf = await api.shelves.get(shelfId);
        const stats = await api.shelves.getStats(shelfId);
        const shelfModalBody = document.getElementById('shelfModalBody');

        let statsHtml = '';
        if (stats.total_books > 0) {
            statsHtml = `
                <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <p><strong>Total Books:</strong> ${stats.total_books}</p>
                    <p><strong>Total Pages:</strong> ${stats.total_pages}</p>
                    <p><strong>Average Pages per Book:</strong> ${stats.avg_pages}</p>
                    <p><strong>Genres:</strong> ${Object.entries(stats.genres).map(([g, c]) => `${g} (${c})`).join(', ')}</p>
                </div>
            `;
        }

        const booksHtml = shelf.books.length > 0
            ? shelf.books.map(book => `
                <div style="padding: 10px; border-bottom: 1px solid #eee;">
                    <strong>${escapeHtml(book.title)}</strong> by ${escapeHtml(book.author)}
                    <button class="btn btn-danger" style="float: right; padding: 5px 10px;" onclick="removeBookFromShelf(${shelfId}, ${book.id})">Remove</button>
                </div>
            `).join('')
            : '<p>No books in this shelf yet.</p>';

        shelfModalBody.innerHTML = `
            <h2>${escapeHtml(shelf.name)}</h2>
            <p><strong>Owner:</strong> ${escapeHtml(shelf.owner)}</p>
            <p><strong>Created:</strong> ${new Date(shelf.created_at).toLocaleDateString()}</p>
            ${statsHtml}
            <h3>Books in this Shelf:</h3>
            <div>${booksHtml}</div>
        `;

        shelfModal.style.display = 'block';
    } catch (error) {
        showAlert(`Error loading shelf details: ${error.message}`, 'error');
    }
}

// Show Add Book to Shelf
async function showAddBookToShelf(shelfId) {
    try {
        const books = await api.books.list({ limit: 100 });
        const shelf = await api.shelves.get(shelfId);

        const availableBooks = books.filter(book => !shelf.books.some(b => b.id === book.id));

        if (availableBooks.length === 0) {
            showAlert('All books are already in this shelf!', 'error');
            return;
        }

        const shelfModalBody = document.getElementById('shelfModalBody');
        shelfModalBody.innerHTML = `
            <h2>Add Book to "${escapeHtml(shelf.name)}"</h2>
            <div>${availableBooks.map(book => `
                <div style="padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>${escapeHtml(book.title)}</strong><br>
                        <small>${escapeHtml(book.author)}</small>
                    </div>
                    <button class="btn btn-success" onclick="addBookToShelf(${shelfId}, ${book.id})">Add</button>
                </div>
            `).join('')}</div>
        `;

        shelfModal.style.display = 'block';
    } catch (error) {
        showAlert(`Error loading books: ${error.message}`, 'error');
    }
}

// Add Book to Shelf
async function addBookToShelf(shelfId, bookId) {
    try {
        await api.shelves.addBook(shelfId, bookId);
        showAlert('Book added to shelf!', 'success');
        shelfModal.style.display = 'none';
        loadBookshelves();
    } catch (error) {
        showAlert(`Error adding book to shelf: ${error.message}`, 'error');
    }
}

// Remove Book from Shelf
async function removeBookFromShelf(shelfId, bookId) {
    if (!confirm('Remove this book from the shelf?')) return;

    try {
        await api.shelves.removeBook(shelfId, bookId);
        showAlert('Book removed from shelf!', 'success');
        loadBookshelves();
        shelfModal.style.display = 'none';
    } catch (error) {
        showAlert(`Error removing book: ${error.message}`, 'error');
    }
}

// Filter Books
async function handleFilterBooks() {
    const author = document.getElementById('authorFilter').value.trim();
    const genre = document.getElementById('genreFilter').value.trim();

    try {
        const params = {};
        if (author) params.author = author;
        if (genre) params.genre = genre;

        booksList.innerHTML = '<p class="loading">Filtering books...</p>';
        const books = await api.books.list(params);

        if (books.length === 0) {
            booksList.innerHTML = '<p class="loading">No books match your filters.</p>';
            return;
        }

        booksList.innerHTML = books.map(book => `
            <div class="book-card" onclick="showBookDetails(${book.id})">
                <h3>${escapeHtml(book.title)}</h3>
                <p class="author">by ${escapeHtml(book.author)}</p>
                <div class="book-meta">
                    <div>📅 ${book.publication_year}</div>
                    <div>📖 ${book.pages} pages</div>
                    <div>ISBN: ${book.isbn}</div>
                </div>
                <span class="book-genre">${escapeHtml(book.genre)}</span>
                <div class="book-actions">
                    <button class="btn btn-secondary" onclick="event.stopPropagation(); deleteBook(${book.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        booksList.innerHTML = `<p class="loading">Error filtering books: ${error.message}</p>`;
    }
}

// Clear Filter
async function handleClearFilter() {
    document.getElementById('authorFilter').value = '';
    document.getElementById('genreFilter').value = '';
    loadBooks();
}

// Show Alert
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    document.body.insertBefore(alertDiv, document.body.firstChild);

    setTimeout(() => alertDiv.remove(), 4000);
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initial Load
window.addEventListener('load', () => {
    loadBooks();
});
