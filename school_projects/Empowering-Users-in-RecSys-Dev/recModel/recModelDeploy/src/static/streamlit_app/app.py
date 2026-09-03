import streamlit as st
import os
import base64
import requests

# Import your page modules
from sections.landing import show_landing
from sections.welcome import show_welcome
from sections.genres import show_genres
from sections.authors import show_authors
from sections.favorite_books import show_favorite_books
from sections.additional_preferences import show_additional_preferences
from sections.completion import show_completion
from sections.profile import show_profile
from sections.saved_for_later import show_saved_for_later
from sections.recommendations import show_recommendations
from sections.how_it_works import show_how_it_works


from utils.profile_utils import load_profile, save_profile, initialize_user_profile

# SESSION INIT
def initialize_session_state():
    if "profile_completed" not in st.session_state:
        st.session_state.profile_completed = False
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "Recommendations"
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}
    if "saved_for_later" not in st.session_state.user_profile:
        st.session_state.user_profile["saved_for_later"] = []
    if "ratings" not in st.session_state.user_profile:
        st.session_state.user_profile["ratings"] = {}
    if "not_interested" not in st.session_state.user_profile:
        st.session_state.user_profile["not_interested"] = []
    if "recommended_history" not in st.session_state.user_profile:
        st.session_state.user_profile["recommended_history"] = []
    if "book_metadata" not in st.session_state:
        st.session_state.book_metadata = {}
    

initialize_session_state()

# PAGE CONFIG
st.set_page_config(
    page_title="BookWise.ai",
    page_icon="assets/book_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed" if not st.session_state.profile_completed else "expanded"
)

# LOAD CSS
def load_css():
    """Load and inject custom CSS for styling."""
    css_file = "static/custom_styles.css"
    if os.path.exists(css_file):
        with open(css_file, "r") as f:
            css_text = f.read()
        st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Warning: CSS file {css_file} not found.")

load_css()

st.markdown("""
<style>
/* Target all sidebar navigation buttons */
[data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
    background-color: #4e7694 !important;
    color: white !important;
    border: none !important;
    font-weight: 500 !important;
}

/* Make the active button red */
[data-testid="stSidebar"] [data-testid="baseButton-primary"] {
    background-color: #4e7694 !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
}

/* Make the sidebar BookWise logo larger */
[data-testid="stSidebar"] div[style*="display: flex; align-items: center"] h2 {
    font-size: 24px !important;
}

[data-testid="stSidebar"] div[style*="display: flex; align-items: center"] img {
    width: 50px !important;
    height: 50px !important;
}
</style>
""", unsafe_allow_html=True)

# HELPER: HEADER
def get_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# API Status Display
def show_api_status():
    """Show API connection status in a small badge"""
    api_connected = check_api_connection()
    connection_status = "🟢 API Connected" if api_connected else "🔴 API Offline"
    
    st.markdown(f"""
        <div style="position: absolute; top: 10px; right: 10px; 
                    background-color: {'rgba(46, 204, 113, 0.2)' if api_connected else 'rgba(231, 76, 60, 0.2)'};
                    padding: 5px 10px; border-radius: 5px; font-size: 12px;">
            {connection_status}
        </div>
    """, unsafe_allow_html=True)

# BOOK ACTION CALLBACKS
def save_book_for_later(book_title):
    # Find the book in recommendations
    book_to_save = None
    new_recommendations = []
    
    for book in st.session_state.recommendations_list:
        if book["title"] == book_title:
            book_to_save = book
        else:
            new_recommendations.append(book)
    
    if book_to_save:
        # Save to saved_for_later
        st.session_state.user_profile["saved_for_later"].append(book_to_save)
        # Update recommendations list
        st.session_state.recommendations_list = new_recommendations
        save_profile()

def check_api_connection():
    """Check if API is accessible"""
    import requests
    try:
        response = requests.get("http://localhost:8000")
        return response.status_code == 200
    except:
        return False
        
def main():

    # Process any pending actions
    if "pending_action" in st.session_state and st.session_state.pending_action:
        action = st.session_state.pending_action
        
        if action["type"] == "save":
            save_book_for_later(action["title"])
        
    initialize_user_profile()
    # Keep load_profile() commented out for local development:
    # load_profile()

    # Show API status in the corner
    show_api_status()

    # STEP-BASED ONBOARDING
    if not st.session_state.profile_completed:
        # For onboarding, we'll show a header since sidebar is hidden
        image_path = os.path.join("assets", "book_icon.png")
        if os.path.exists(image_path):
            image_base64 = get_image_base64(image_path)
            st.markdown(f"""
                <div class="app-header">
                    <div class="header-left">
                        <img src="data:image/png;base64,{image_base64}" class="header-icon"/>
                        <h2 style="color: #FFF;">BookWise</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Hide sidebar during onboarding
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if "page" not in st.session_state:
            st.session_state.page = "landing"  # Start with landing page instead of welcome

        sections = {
            "landing": show_landing,  # Add landing page to sections
            "welcome": show_welcome,
            "genres": show_genres,
            "authors": show_authors,
            "favorite_books": show_favorite_books,
            "additional_preferences": show_additional_preferences,
            "completion": show_completion
        }

        sections[st.session_state.page]()

    # POST-ONBOARDING INTERFACE WITH SIDEBAR
    else:
        # Sidebar 
        with st.sidebar:
            image_path = os.path.join("assets", "book_icon.png")
            if os.path.exists(image_path):
                image_base64 = get_image_base64(image_path)
                st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <img src="data:image/png;base64,{image_base64}" style="width: 60px; height: 60px; margin-right: 15px;"/>
                        <h2 style="margin: 0; padding: 0; color: #9C897E; font-size: 28px;">BookWise</h2>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.title("BookWise")
            
            # Show user name if available
            user_name = st.session_state.user_profile.get("name", "")
            if user_name:
                st.write(f"Welcome, {user_name}!")
            
            st.markdown("---")
            
            # Wrap buttons in the sidebar-nav class
            st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
            
            # Determine button types based on the selected tab
            rec_type = "primary" if st.session_state.selected_tab == "Recommendations" else "secondary"
            profile_type = "primary" if st.session_state.selected_tab == "Profile" else "secondary"
            library_type = "primary" if st.session_state.selected_tab == "Library" else "secondary"
            howit_type = "primary" if st.session_state.selected_tab == "How It Works" else "secondary"
            
            # Create the navigation buttons
            if st.button("Recommendations", key="nav_recommendations", use_container_width=True, type=rec_type):
                st.session_state.selected_tab = "Recommendations"
                st.rerun()
                
            if st.button("Profile", key="nav_profile", use_container_width=True, type=profile_type):
                st.session_state.selected_tab = "Profile"
                st.rerun()
                
            if st.button("Library", key="nav_library", use_container_width=True, type=library_type):
                st.session_state.selected_tab = "Library"
                st.rerun()

            if st.button("How It Works", key="nav_howit", use_container_width=True, type=howit_type):
                st.session_state.selected_tab = "How It Works"
                st.rerun()
            
            # Close the sidebar-nav container
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Main content area without the header
        selected_tab = st.session_state.selected_tab
        
        # Show content based on selected tab
        if selected_tab == "Recommendations":
            show_recommendations()
        elif selected_tab == "Profile":
            show_profile()
        elif selected_tab == "Library":
            show_saved_for_later()
        elif selected_tab == "How It Works":
            show_how_it_works() 

if __name__ == "__main__":
    main()