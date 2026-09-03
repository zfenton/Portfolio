import streamlit as st
from utils.data_utils import get_unique_genres, get_unique_authors, get_unique_books
import time

def show_welcome():
    st.title("Welcome to BookWise!")
    st.write("""
    Let's help you discover your next great read. In just a few minutes, we can learn about your reading preferences to provide personalized recommendations tailored just for you.

    We'll ask you a few quick questions about what you enjoy reading. Feel free to be as specific or general as you'd like—there are no wrong answers!
    """)
    
    name = st.text_input("What's your name?", key="user_name", value=st.session_state.user_profile.get("name", ""))
    
    if "loading_data" not in st.session_state:
        st.session_state.loading_data = False
    

    start_disabled = not name.strip() or st.session_state.loading_data
    
    # Create containers for all UI elements
    button_container = st.empty()
    loading_container = st.empty()
    progress_container = st.empty()
    message_container = st.empty()  
    
    # Show button only if not loading
    if not st.session_state.loading_data:
        button_label = "Let's Get Started!"
        if not name.strip():
            button_label += " (Please enter your name first)"
        
        if button_container.button(button_label, disabled=start_disabled):
            st.session_state.user_profile["name"] = name
            
            st.session_state.loading_data = True
            
            st.rerun()
    
    # If we're in loading state, show loading UI and process data
    if st.session_state.loading_data:
        button_container.empty()
        
        # Show loading message
        loading_container.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h2 style="color: #4e7694;">Preparing your personalized experience...</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize progress bar
        progress_bar = progress_container.progress(0)
        
        try:

            message_container.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <h3 style="color: #666; font-size: 24px; font-weight: bold;">Loading genre data...</h3>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(10)
            genres = get_unique_genres()
            
            # Loading authors with large text message
            message_container.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <h3 style="color: #666; font-size: 24px; font-weight: bold;">Loading author data...</h3>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(40)
            authors = get_unique_authors()
            
            # Loading books with large text message
            message_container.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <h3 style="color: #666; font-size: 24px; font-weight: bold;">Loading book data...</h3>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(70)
            books = get_unique_books()
            
            # Finalizing with large text message
            message_container.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <h3 style="color: #666; font-size: 24px; font-weight: bold;">Finalizing your profile...</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Complete the progress bar
            for percent in range(70, 101, 5):
                time.sleep(0.1)
                progress_bar.progress(percent)
            
            st.session_state.loading_data = False
            st.session_state.page = "genres"
            st.rerun()
        
        except Exception as e:
            loading_container.error(f"Error loading data: {str(e)}")
            st.session_state.loading_data = False
            button_container.button("Try Again", key="retry_button")