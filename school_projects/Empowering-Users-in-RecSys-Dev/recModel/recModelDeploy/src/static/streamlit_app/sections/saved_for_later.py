import streamlit as st
from streamlit_star_rating import st_star_rating
from utils.book_cover_utils import get_cover_image_url

def show_saved_for_later():
    st.subheader("Your Library")

    # Ensure user_profile and saved_for_later exist
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}
    if "saved_for_later" not in st.session_state.user_profile:
        st.session_state.user_profile["saved_for_later"] = []

    saved_books = st.session_state.user_profile["saved_for_later"]

    if not saved_books:
        st.info("You haven't saved any books yet! Go to the 'Recommendations' tab to add books to your library.")
        return

    # Display saved books in columns (up to 3 per row)
    max_cols = min(len(saved_books), 3)
    cols = st.columns(max_cols)

    for idx, book in enumerate(saved_books):
        with cols[idx % max_cols]:
            with st.container():
                # Get the cover image URL for this book
                cover_url = get_cover_image_url(book['title'])
                
                st.markdown(f"""
                <div class="recommendation-card">
                    <div class="card-content">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <img src="{cover_url}"
                                 style="width: 80px; height: auto; margin-right: 15px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />
                            <h4 style="margin: 0;">
                                <span style="color:#4e7694;">♦</span> {book['title']}
                            </h4>
                        </div>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Description:</strong> {book['description']}</p>
                        <p><strong>Why this was recommended:</strong> {book['explanation']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Show star rating for "Read it?"
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
                        key=f"rating_{book['title']}",
                        dark_theme=False,
                        customCSS=".react-stars {margin-top: -15px; background-color: #E6E3DC !important; color: #9C897E;}"
                    )

                if rating > 0:
                    # Save the rating
                    if "ratings" not in st.session_state.user_profile:
                        st.session_state.user_profile["ratings"] = {}
                    st.session_state.user_profile["ratings"][book["title"]] = rating
                    st.session_state.user_profile["saved_for_later"] = [
                        b for b in saved_books if b["title"] != book["title"]
                    ]
                    st.rerun()

                # "No Longer Interested" button
                if st.button("✗ No Longer Interested", key=f"lib_not_int_{book['title']}"):
                    if "not_interested" not in st.session_state.user_profile:
                        st.session_state.user_profile["not_interested"] = []
                    st.session_state.user_profile["not_interested"].append(book["title"])

                    # Remove from saved_for_later
                    st.session_state.user_profile["saved_for_later"] = [
                        b for b in saved_books if b["title"] != book["title"]
                    ]
                    st.rerun()
