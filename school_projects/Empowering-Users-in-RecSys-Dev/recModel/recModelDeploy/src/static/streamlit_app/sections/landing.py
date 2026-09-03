# sections/landing.py
import streamlit as st
import os

def show_landing():
    # Check for navigation
    if "navigate_to_welcome" in st.session_state and st.session_state.navigate_to_welcome:
        st.session_state.navigate_to_welcome = False
        st.session_state.page = "welcome"
        st.rerun()

    # Gradient background and header styling
    st.markdown(
        """
        <style>
        /* Gradient background for the entire page */
        .stApp {
            background: linear-gradient(to bottom, #f5f2eb, #b6b3ac) !important;
        }
        
        /* Make header extend fully to edges */
        .app-header {
            padding: 15px 40px;
            background-color: #9C897E;
            width: 100vw !important;
            margin-left: calc(-50vw + 50%);
            margin-right: calc(-50vw + 50%);
            margin-top: -3rem !important;  /* Push up to cover the top space */
            padding-top: 3rem !important;  /* Add padding to compensate */
            margin-bottom: 20px;
            position: relative;
            z-index: 999;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create the layout
    col1, spacing, col2 = st.columns([3, 0.5, 4])
    
    # Left side - Image
    with col1:
        landing_image_path = os.path.join("assets", "landing_books.png")
        if os.path.exists(landing_image_path):
            st.image(landing_image_path, use_container_width=True)
        else:
            st.error("Landing image not found. Please check the file path.")
    
    # Right side - Content
    with col2:
        st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
        st.markdown('<h1 style="font-size: 75px; font-weight: 750; margin-bottom: 35px;">A New Chapter in Book Recommendations</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 24px; line-height: 1.6; margin-bottom: 40px; color: #555;">We don\'t just help you find what to read next – we explain why it matches your unique preferences and empower you to refine your recommendations.</p>', unsafe_allow_html=True)
        
        st.markdown(
            """
            <style>
            /* Extremely specific selector to override any other styles */
            body .element-container:has(button) div.stButton > button {
                background-color: #4e7694 !important;
                color: white !important;  /* Ensuring white text */
                font-size: 24px !important;  /* Increased text size */
                height: auto !important;
                padding: 16px 32px !important;
                border-radius: 50px !important;
                border: none !important;
                font-weight: bold !important;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
            }
            
            /* Hover state */
            body .element-container:has(button) div.stButton > button:hover {
                background-color: #3c5a75 !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
            }
            
            /* Active state */
            body .element-container:has(button) div.stButton > button:active {
                transform: translateY(1px) !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("Find Your Next Read"):
            st.session_state.navigate_to_welcome = True
            st.rerun()