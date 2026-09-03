import streamlit as st
from utils.profile_utils import save_profile

def show_additional_preferences():
    st.title("Additional Reading Preferences")
    
    current_preferences = st.session_state.user_profile.get("additional_preferences", "")
    
    preferences = st.text_area(
        "Is there anything else you'd like to tell us about your reading preferences? Share as much as you'd like.",
        value=current_preferences,
        height=150,
        placeholder="For example: I prefer books with happy endings, I like books that are considered literary classics, I enjoy books with strong female protagonists, etc."
    )
    
    # Navigation buttons
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("← Back"):
            st.session_state.user_profile["additional_preferences"] = preferences
            st.session_state.page = "favorite_books"
            st.rerun()
    with col2:
        if st.button("Next →"):
            # Save preferences
            st.session_state.user_profile["additional_preferences"] = preferences
            save_profile()
            st.session_state.page = "completion"
            st.rerun()