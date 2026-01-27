// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// API Helper Functions
const api = {
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, {
                ...defaultOptions,
                ...options,
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error: ${error.message}`);
            throw error;
        }
    },

    // Books API
    books: {
        list: (params = {}) => {
            const queryString = new URLSearchParams(params).toString();
            const endpoint = `/books${queryString ? '?' + queryString : ''}`;
            return api.request(endpoint);
        },

        get: (id) => api.request(`/books/${id}`),

        create: (data) => api.request('/books', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

        update: (id, data) => api.request(`/books/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),

        delete: (id) => api.request(`/books/${id}`, {
            method: 'DELETE',
        }),
    },

    // Bookshelves API
    shelves: {
        list: () => api.request('/bookshelves'),

        get: (id) => api.request(`/bookshelves/${id}`),

        create: (name, owner) => api.request('/bookshelves', {
            method: 'POST',
            body: JSON.stringify({ name, owner }),
        }),

        addBook: (shelfId, bookId) => api.request(
            `/bookshelves/${shelfId}/books/${bookId}`,
            { method: 'POST' }
        ),

        removeBook: (shelfId, bookId) => api.request(
            `/bookshelves/${shelfId}/books/${bookId}`,
            { method: 'DELETE' }
        ),

        getStats: (id) => api.request(`/bookshelves/${id}/stats`),
    },
};
