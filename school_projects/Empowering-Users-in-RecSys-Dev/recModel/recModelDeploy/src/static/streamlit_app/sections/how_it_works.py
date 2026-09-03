# sections/how_it_works.py
import streamlit as st

def show_how_it_works():
    st.markdown("""
    ## Who We Are 
    Our mission at BookWise is to bring the excitement and joy back to reading by providing insightful recommendations and empowering users.
    
    ---
    ## Our Recommendation Process
    BookWise uses a combination of your reading preferences and advanced AI technology 
    to create personalized book recommendations:

    **Preference Collection**: When you first sign up, we ask about your favorite genres, 
    authors, and books to understand your reading tastes.

    **AI-Powered Recommendations**: Our recommendation engine analyzes your preferences 
    to find books that match your unique reading profile.

    **Personalized Explanations**: For every recommendation, we provide a custom 
    explanation of why we think you'll enjoy that particular book, connecting it 
    to your preferences.

    **Continuous Learning**: As you interact with recommendations (saving to your 
    library, marking as "not interested," or rating books), our system learns 
    more about your preferences to improve future suggestions.

    ---
    ## Using BookWise
    **Navigation**
    - **Recommendations**: View your personalized book recommendations.
    - **Profile**: Review and modify your reading preferences. These allows us to customize book selections for you. 
    - **Library**: Access books you've saved for later reading.

    **Interacting with Recommendations**
    - **Save to Library**: Add the book to your library to save your selection for later.
    - **Not Interested**: Let us know the book doesn't appeal to you.
    - **Rate Books**: If you've already read a recommended book, rate it 
      to help us better understand your preferences.

    **Your Feedback Matters**  
    The more you interact with BookWise, the better our recommendations become. 
    Each time you save, rate, or dismiss a book, you're helping the system 
    understand your unique reading tastes.

    **Privacy & Data**  
    BookWise only uses your reading preferences and interactions to improve your 
    personal recommendations. Your reading profile is unique to you and helps us 
    tailor suggestions to your specific interests.

    ---
    Start exploring your personalized recommendations today and discover 
    books that resonate with your unique reading journey!
    """)
