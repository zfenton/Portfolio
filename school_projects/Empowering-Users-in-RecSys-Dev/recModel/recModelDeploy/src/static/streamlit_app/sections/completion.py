import streamlit as st
import time
from utils.profile_utils import save_profile
from sections.recommendations import get_new_recommendations

def show_completion():
    # Create placeholders for all elements
    success_message = st.empty()
    loading_container = st.empty()
    header_container = st.empty()
    subtitle_container = st.empty()
    animation_container = st.empty()
    button_container = st.empty()
    
    # Display initial success message
    with success_message:
        st.success("""
        Thanks for telling us about your reading preferences!
        """)

    if "initial_recommendations_loaded" not in st.session_state:
        with header_container:
            st.markdown("<h2 style='text-align: center; color: #4e7694;'>Preparing your personalized recommendations...</h2>", unsafe_allow_html=True)
        
        with subtitle_container:
            st.markdown("<p style='text-align: center;'>We're analyzing your preferences to find the best matches for you.</p>", unsafe_allow_html=True)
            
        with animation_container:
            st.markdown("""
                <div style="display: flex; justify-content: center; margin: 30px 0;">
                    <div class="book">
                        <div class="book__page"></div>
                        <div class="book__page"></div>
                        <div class="book__page"></div>
                    </div>
                </div>
                <style>
                    .book {
                        width: 100px;
                        height: 120px;
                        position: relative;
                        perspective: 800px;
                    }
                    .book__page {
                        position: absolute;
                        width: 100%;
                        height: 100%;
                        top: 0;
                        left: 0;
                        background-color: #4e7694;
                        transform-origin: left center;
                        transition: transform 0.8s ease-in-out;
                        border-radius: 5px;
                        box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
                    }
                    .book__page:nth-child(1) {
                        animation: flipPage1 3s infinite;
                    }
                    .book__page:nth-child(2) {
                        animation: flipPage2 3s infinite;
                    }
                    .book__page:nth-child(3) {
                        animation: flipPage3 3s infinite;
                    }
                    @keyframes flipPage1 {
                        0%, 20% { transform: rotateY(0deg); }
                        30%, 70% { transform: rotateY(-130deg); }
                        80%, 100% { transform: rotateY(0deg); }
                    }
                    @keyframes flipPage2 {
                        0%, 30% { transform: rotateY(0deg); }
                        40%, 80% { transform: rotateY(-130deg); }
                        90%, 100% { transform: rotateY(0deg); }
                    }
                    @keyframes flipPage3 {
                        0%, 40% { transform: rotateY(0deg); }
                        50%, 90% { transform: rotateY(-130deg); }
                        100% { transform: rotateY(0deg); }
                    }
                </style>
                """, unsafe_allow_html=True)

        # Save profile and get initial recommendations
        save_profile()
        from utils.api_client import get_recommendations
        
        # Load recommendations 
        try:
            st.session_state.recommendations_list = get_recommendations() 
            st.session_state.original_batch_size = len(st.session_state.recommendations_list)
            st.session_state.initial_recommendations_loaded = True
            
            # Add recommendations to history
            from utils.profile_utils import add_to_recommendation_history
            for book in st.session_state.recommendations_list:
                add_to_recommendation_history(book)
                
            st.rerun()
        except Exception as e:
            st.error(f"There was an issue loading recommendations. Please try again. Error: {str(e)}")
            return
    else:
        # Clear the success message for the ready state
        success_message.empty()
        
        # Show the ready state
        with header_container:
            st.markdown("<h2 style='text-align: center; color: #4e7694;'>Your BookWise profile is ready!</h2>", unsafe_allow_html=True)
        
        with subtitle_container:
            st.markdown("<p style='text-align: center;'>We're excited to show you personalized recommendations based on your preferences.</p>", unsafe_allow_html=True)

    # Show the Enter button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if button_container.button("Enter BookWise!", type="primary", use_container_width=True):
            st.session_state.profile_completed = True
            st.session_state.selected_tab = "Recommendations"
            st.rerun()