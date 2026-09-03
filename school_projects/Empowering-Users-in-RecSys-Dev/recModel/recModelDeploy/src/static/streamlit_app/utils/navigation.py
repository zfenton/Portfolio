import streamlit as st

def navigate_to(page_name: str):
    """
    Updates st.session_state.page and forces a rerunl.
    """
    st.session_state.page = page_name
    st.rerun()
