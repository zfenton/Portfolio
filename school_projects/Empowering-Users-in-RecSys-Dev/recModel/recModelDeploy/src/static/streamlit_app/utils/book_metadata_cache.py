import streamlit as st
import logging

logger = logging.getLogger(__name__)
    
def get_book_metadata(title):
    if "book_metadata" not in st.session_state:
        st.session_state.book_metadata = {}

    keys = list(st.session_state.book_metadata.keys())
    
    return st.session_state.book_metadata[title]
  
def update_book_metadata(title, metadata):
    if not isinstance(metadata, dict):
        return  
    
    if "book_metadata" not in st.session_state:
        st.session_state.book_metadata = {}

    existing = st.session_state.book_metadata.get(title)

    # Skip overwrite if existing metadata has a valid genre
    if existing and existing.get("genre") != "Unknown Genre":
        return

    # Skip overwrite if new metadata has missing or bad genre
    if metadata.get("genre") == "Unknown Genre":
        return

    # Write the good metadata
    st.session_state.book_metadata[title] = metadata