import streamlit as st
from utils.data_utils import get_unique_authors
from utils.profile_utils import save_authors

def show_authors():
    st.title("Select Your Favorite Authors")

    default_authors = get_unique_authors()
    current_authors = st.session_state.user_profile.get("authors", [])

    # Single form with two form_submit_buttons:
    with st.form("authors_form"):
        st.write("Pick your favorites from our available authors, then click to proceed.")

        # Multi-select with no typed input allowed
        selected_authors = st.multiselect(
            "Which authors do you enjoy reading?",
            options=default_authors,
            default=current_authors
        )

        col1, col2 = st.columns([1,3])
        with col1:
            back_clicked = st.form_submit_button("← Back")
        with col2:
            next_clicked = st.form_submit_button("Next →")

    # If user clicked "← Back" in the form
    if back_clicked:
        # Save the updated picks
        save_authors(selected_authors)
        st.session_state.page = "genres" 
        st.rerun()

    # If user clicked "Next →" in the form
    if next_clicked:
        save_authors(selected_authors)
        # Navigate to the next page
        st.session_state.page = "favorite_books"
        st.rerun()
