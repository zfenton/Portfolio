# utils/data_utils.py

import streamlit as st
from utils.api_client import get_genres, get_authors, get_books, get_recommendations 
import logging
import requests

logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_books():
    """
    Get all unique books from the API.
    Falls back to hardcoded values if API call fails.
    Also updates the session state with book metadata if available.
    """
    books = get_books()

    if books and isinstance(books, dict):
        book_list = books.get("books", [])
        metadata_list = books.get("metadata", [])

        # Ensure metadata cache is initialized
        if "book_metadata" not in st.session_state:
            st.session_state.book_metadata = {}

        for book in metadata_list:
            title = book.get("title", "").strip()
            author = book.get("author", "").strip()
            genre = book.get("genre", "Unknown Genre").strip()

            metadata = {
                "title": title,
                "author": author,
                "genre": genre
            }

            # Cache with plain title
            st.session_state.book_metadata[title] = metadata

            # Cache with display format
            display_key = f"{title} - {author}"
            st.session_state.book_metadata[display_key] = metadata

        return book_list

    # Fallback if API call fails or structure is unexpected
    return [
        "To Kill a Mockingbird - Harper Lee",
        "1984 - George Orwell",
        "Pride and Prejudice - Jane Austen",
        "The Great Gatsby - F. Scott Fitzgerald",
        "Moby Dick - Herman Melville"
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_genres():
    """
    Get all unique genres from the API.
    Falls back to hardcoded values if API call fails.
    """
    genres = get_genres()
    if not genres:
        # Fallback to hardcoded genres if API call fails
        return [
            "Fiction", "Non-Fiction", "Mystery", "Fantasy",
            "Science Fiction", "Romance", "History"
        ]
    return genres

@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_authors():
    """
    Get all unique authors from the API.
    Falls back to hardcoded values if API call fails.
    """
    authors = get_authors()
    if not authors:
        # Fallback to hardcoded authors if API call fails
        return [
            "J.K. Rowling", "Stephen King", "Jane Austen",
            "Agatha Christie", "Neil Gaiman", "George R.R. Martin"
        ]
    return authors
