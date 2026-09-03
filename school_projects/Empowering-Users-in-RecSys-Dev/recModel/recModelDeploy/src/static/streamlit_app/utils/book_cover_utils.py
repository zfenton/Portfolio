import streamlit as st
import pandas as pd
import logging
from utils.api_client import get_book_covers

# Base URL for S3 bucket
S3_BASE_URL = "https://w210recsys.s3.us-east-1.amazonaws.com/book_clean/"

# Default image to use when a match isn't found
DEFAULT_COVER = "book_covers/1_000_Questions_of_Who_You_Are_and_Your_View_on_Life.jpg"

@st.cache_data(ttl=3600, show_spinner=False)
def get_cover_lookup_table():
    """
    Get the book covers lookup table via the API with caching
    """
    covers = get_book_covers()
    if not covers:
        logging.warning("No book covers found via API")
        return pd.DataFrame()
    return pd.DataFrame(covers)

def get_cover_image_url(book_title):
    """
    Look up a book cover image URL by title using exact case-sensitive matching
    
    Args:
        book_title: The title of the book
        
    Returns:
        URL to the book cover image, or the default cover if not found
    """
    # Get the lookup table
    covers_df = get_cover_lookup_table()
    
    # Use exact case-sensitive matching
    match = covers_df[covers_df['title'] == book_title]
    
    if not match.empty:
        image_path = match.iloc[0]['image_path']
        full_url = f"{S3_BASE_URL}{image_path}" if image_path else f"{S3_BASE_URL}{DEFAULT_COVER}"
        return full_url
    
    # No match found, return default cover
    return f"{S3_BASE_URL}{DEFAULT_COVER}"
