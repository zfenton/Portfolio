# pages/recommendations.py
import streamlit as st
from streamlit_star_rating import st_star_rating
from utils.profile_utils import save_profile, add_to_recommendation_history
from utils.book_cover_utils import get_cover_image_url


def get_new_recommendations():
    """Get fresh recommendations based on current user profile"""
    # Force a new API call with the latest profile data
    from utils.api_client import get_recommendations
    
    # Get fresh recommendations directly from API, bypassing cache
    all_recommendations = get_recommendations() 
    
    # Process already seen books 
    already_seen_titles = []
    if "not_interested" in st.session_state.user_profile:
        already_seen_titles.extend(st.session_state.user_profile["not_interested"])
    if "ratings" in st.session_state.user_profile:
        already_seen_titles.extend(st.session_state.user_profile["ratings"].keys())
    if "saved_for_later" in st.session_state.user_profile:
        for book in st.session_state.user_profile["saved_for_later"]:
            if "title" in book:
                already_seen_titles.append(book["title"])
    
    # Filter out already seen books
    new_recommendations = [r for r in all_recommendations if r["title"] not in already_seen_titles]
    
    # Add new recommendations to history
    for book in new_recommendations[:6]:
        add_to_recommendation_history(book)
    
    return new_recommendations[:6]


def show_ratings(book_title, key_prefix):
    """Display 5-star rating widget and handle selection"""
    st.write("Rate this book:")
    
    cols = st.columns(5)
    rating = 0
    
    # Create 5 star buttons
    for i in range(5):
        star_num = i + 1
        with cols[i]:
            if st.button("★", key=f"{key_prefix}_star_{star_num}_{book_title}"):
                rating = star_num
                
                # Initialize ratings dictionary if it doesn't exist
                if "ratings" not in st.session_state.user_profile:
                    st.session_state.user_profile["ratings"] = {}
                
                # Save the rating
                st.session_state.user_profile["ratings"][book_title] = rating
                
                # Remove from recommendations
                st.session_state.recommendations_list = [
                    book for book in st.session_state.recommendations_list 
                    if book["title"] != book_title
                ]
                st.rerun()




def show_recommendations():
    st.subheader("Your Book Recommendations")

    if "recommendations_list" not in st.session_state:
        st.session_state.recommendations_list = get_new_recommendations()

        for book in st.session_state.recommendations_list:
            add_to_recommendation_history(book)

    # Initialize loading state if it doesn't exist
    if "loading_recommendations" not in st.session_state:
        st.session_state.loading_recommendations = False
        
    # Get current recommendations and count how many are remaining
    current_recommendations = st.session_state.recommendations_list
    remaining = len(current_recommendations)

    # Store the original batch size if not already stored
    if "original_batch_size" not in st.session_state:
        st.session_state.original_batch_size = remaining
    original_batch_size = st.session_state.original_batch_size

    # Calculate viewed count for progress
    viewed = original_batch_size - remaining

    # Display message about recommendation batches
    st.markdown(f"""
    <div style="margin-bottom: 20px; background-color: #e8f4f8; padding: 15px; border-radius: 5px; border-left: 4px solid #4e7694;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <p style="margin: 0; font-weight: 500;">You have <strong>{remaining}</strong> recommendation{'' if remaining == 1 else 's'} left in this batch.</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em;">A new batch of recommendations will be generated after you've evaluated all current suggestions.</p>
            </div>
            <div style="min-width: 120px; text-align: right;">
                <span style="font-size: 1.2em; font-weight: bold; color: #4e7694;">{viewed} of {original_batch_size} evaluated</span>
            </div>
        </div>
        <div style="margin-top: 10px; background-color: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
            <div style="background-color: #4e7694; width: {(viewed/original_batch_size)*100 if original_batch_size > 0 else 0}%; height: 100%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write('''Below are three personalized recommendations from your current batch, 
    each with an explanation about why we think you'll like it. 
    As you evaluate them, new recommendations from the batch will automatically appear.
    Once you've evaluated this batch, click 'Get More Recommendations' for a new one that reflects your updated preferences.''')
    
    recommendations = st.session_state.recommendations_list
    
    if not recommendations:
        st.info("You've gone through your latest batch of recommendations! Click below for a new one.")
        
        # Create placeholders for all elements
        button_container = st.empty()
        info_container = st.empty()
        animation_container = st.empty()
        
        # Check if in loading state
        if "loading_recommendations" not in st.session_state:
            st.session_state.loading_recommendations = False
        
        # Show either button or loading animation based on state
        if not st.session_state.loading_recommendations:
            # Show the button when not loading
            if button_container.button("Get More Recommendations"):
                # Set loading state
                st.session_state.loading_recommendations = True
                st.rerun()
        else:
            # Show loading animation and hide button
            with info_container:
                st.success("Generating new personalized recommendations based on your preferences...")
                
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
                
            # Actually get the recommendations
            st.session_state.recommendations_list = get_new_recommendations()
            st.session_state.original_batch_size = len(st.session_state.recommendations_list)
            
            # Reset loading state
            st.session_state.loading_recommendations = False
            st.rerun()
        return
    
    # Only display up to 3 recommendations at a time
    display_recommendations = recommendations[:3]
    
    # Display recommendations in columns
    max_cols = len(display_recommendations)
    cols = st.columns(max_cols)
    
    for idx, rec in enumerate(display_recommendations):
        with cols[idx]:
            with st.container():
                # Get cover image URL for this book
                cover_url = get_cover_image_url(rec['title'])
                
                # # Card styling with HTML          
                st.markdown(f"""
                <div class="recommendation-card">
                    <div class="card-content">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <img src="{cover_url}" 
                                style="width: 80px; height: auto; margin-right: 15px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />
                            <h4 style="margin: 0;"><span style="color:#4e7694;">♦</span> {rec['title']}</h4>
                        </div>
                        <p><strong>Author:</strong> {rec['author']}</p>
                        <p><strong>Description:</strong> {rec['description']}</p>
                        <p><strong>Why this was recommended:</strong> {rec['explanation']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons
                if st.button("Save to Library", key=f"save_{rec['title']}"):
                    # Set pending action to be processed in main app loop
                    st.session_state.pending_action = {
                        "type": "save",
                        "title": rec["title"]
                    }
                    st.rerun()
                                
                if st.button("✗ Not Interested", key=f"not_int_{rec['title']}"):
                    if "not_interested" not in st.session_state.user_profile:
                        st.session_state.user_profile["not_interested"] = []
                    
                    # Add just the title for consistency
                    st.session_state.user_profile["not_interested"].append(rec["title"])
                    
                    # Then also call save_profile to persist changes
                    from utils.profile_utils import save_profile
                    save_profile()

                    # Remove from recommendations
                    st.session_state.recommendations_list = [
                        book for book in recommendations if book["title"] != rec["title"]
                    ]
                    st.rerun()

                # Two columns: first for the label, second for the star widget
                col_label, col_stars = st.columns([1.1, 1])  

                with col_label:
                    st.markdown("""
                        <div style="display: flex; height: 40px; align-items: center; justify-content: center; text-align: center;">
                            <p style="margin: 0; padding: 0;">Already read it? Rate it:</p>
                        </div>
                    """, unsafe_allow_html=True)

                with col_stars:
                    rating = st_star_rating(
                        label="",
                        maxValue=5,
                        defaultValue=0,
                        key=f"rating_{rec['title']}",
                        dark_theme=False,
                        customCSS=".react-stars {margin-top: -15px; background-color: #E6E3DC !important; color: #9C897E;}"
                    )

                    if rating > 0:
                        if "ratings" not in st.session_state.user_profile:
                            st.session_state.user_profile["ratings"] = {}
                        
                        # Use just the title for the key
                        st.session_state.user_profile["ratings"][rec["title"]] = rating
                        
                        # Save to profile 
                        from utils.profile_utils import save_profile
                        save_profile()
                        
                        # Remove from recommendations
                        st.session_state.recommendations_list = [
                            book for book in recommendations if book["title"] != rec["title"]
                        ]
                        st.rerun()