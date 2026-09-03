import streamlit as st
from utils.data_utils import get_unique_books
from utils.profile_utils import save_favorite_books

def show_favorite_books():
    st.title("Select Your Favorite Books")

    default_books = get_unique_books()
    current_books = st.session_state.user_profile.get("favorite_books", [])

    with st.form("favorite_books_form"):
        st.write("Select multiple favorite books from our available titles - adding more helps us find better matches for you.")

        # Multi-select with no typed input
        selected_books = st.multiselect(
            "Which books do you enjoy?",
            options=default_books,
            default=current_books
        )

        col1, col2 = st.columns([1,3])
        with col1:
            back_clicked = st.form_submit_button("← Back")
        with col2:
            next_clicked = st.form_submit_button("Next →")

    # If user clicked "← Back"
    if back_clicked:
        save_favorite_books(selected_books)
        st.session_state.page = "authors" 
        st.rerun()

    # If user clicked "Next →"
    if next_clicked:
        save_favorite_books(selected_books)
        st.session_state.page = "additional_preferences" 
        st.rerun()

