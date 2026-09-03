import streamlit as st
from utils.data_utils import get_unique_genres
from utils.profile_utils import save_genres

def show_genres():
    st.title("Select Your Favorite Genres")

    default_genres = get_unique_genres()
    current_genres = st.session_state.user_profile.get("genres", [])
    current_disliked = st.session_state.user_profile.get("disliked_genres", [])

    with st.form("genres_form", clear_on_submit=False):
        st.write("Choose your preferred genres from our available categories, then click to proceed.")

        # Multi-select for liked genres
        selected_genres = st.multiselect(
            "Which genres do you enjoy reading?",
            options=default_genres,
            default=current_genres
        )
        
        st.write("---")
        
        # Multi-select for disliked genres
        st.write("You can also tell us about genres you'd prefer to avoid. This is optional, but helps us provide better recommendations.")
        disliked_genres = st.multiselect(
            "Which genres would you prefer not to see in your recommendations?",
            options=default_genres,
            default=current_disliked
        )

        # Two big form-submit buttons
        col1, col2 = st.columns([1,3])
        with col1:
            back_clicked = st.form_submit_button("← Back")
        with col2:
            next_clicked = st.form_submit_button("Next →")

    # If the user clicked "← Back"
    if back_clicked:
        save_genres(selected_genres, disliked_genres)
        st.session_state.page = "welcome"
        st.rerun()

    # If the user clicked "Next →"
    if next_clicked:
        save_genres(selected_genres, disliked_genres)
        st.session_state.page = "authors"
        st.rerun()