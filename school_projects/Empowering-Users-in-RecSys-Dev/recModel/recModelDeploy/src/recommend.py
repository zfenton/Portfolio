# Embeddings to Recommendations

# Imports
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import logging
from src.bookEmbeddings import load_book_embeddings
import sagemaker
import boto3
import pandas as pd
from src.pcaEmbeddings import calculate_pca_embeddings, calculate_user_pca_embeddings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def recommend(user_embedding, filter_info, top_k=6, path='embeddings/book_embeddings.npy'):
    """
    Recommend top_k books based on cosine similarity using book embeddings.
    :param filter: Dictionary with 'keep' and 'remove' filters.
    :param input_book_title: Title of the book to find recommendations for.
    :param top_k: Number of recommendations to return.
    :param path: Path to embeddings if they need to be loaded.
    :return: DataFrame with top_k recommendations.
    """
    s3_bucket = "w210recsys"
    
    # Older paths for original dataset
    # aws_book_embeddings_path = "model/recModel/modelFiles/book_embeddings.npy" 
    # aws_books_df_path = "model/recModel/modelFiles/books_df.csv"
    
    # Newer paths for cleaned dataset
    aws_book_embeddings_path = "model/recModel/modelFiles/book_embeddings.npy"
    aws_books_df_path = "book_clean/books_data_clean.pkl"
    
    full_book_embeddings = None
    
    if os.path.exists("src/static/full_book_embeddings.pkl"):
        full_book_embeddings = pd.read_pickle('src/static/full_book_embeddings.pkl') # unique book titles/keys
    else:
        full_book_embeddings = load_book_embeddings(s3_bucket, aws_book_embeddings_path, aws_books_df_path)
        
    if os.path.exists("src/static/pca_transformed_book_embeddings.pkl"):
        pca_transformed_book_embeddings = pd.read_pickle('src/static/pca_transformed_book_embeddings.pkl') # Create this!
    else:
        pca_transformed_book_embeddings = calculate_pca_embeddings(full_book_embeddings)
   
    # Apply filtering logic
    full_book_embeddings_copy = full_book_embeddings.copy()
    #print(f"full_book_embeddings_copy columns: {full_book_embeddings_copy.columns}")
    
    # Apply 'keep' filters
    for key, value_set in filter_info.get('keep', {}).items():
        if value_set:
            full_book_embeddings_copy = full_book_embeddings_copy[
                full_book_embeddings_copy[key].isin(value_set)]
    
    # Apply 'remove' filters
    for key, value_set in filter_info.get('remove', {}).items():
        if value_set:
            full_book_embeddings_copy = full_book_embeddings_copy[
                ~full_book_embeddings_copy[key].isin(value_set)]
    
    # Get book embeddings (make sure to extract relevant embeddings)
    book_embeddings = np.vstack(full_book_embeddings_copy['embeddings'].values)
    user_embedding_2d = np.expand_dims(user_embedding, axis=0)

    # Compute Cosine Similarity between user and book embeddings
    similarity_scores = cosine_similarity(user_embedding_2d, book_embeddings)
    print(f"Similarity Scores: \n{similarity_scores}\n")
    print(f"Similarity Scores Shape: {similarity_scores.shape}\n")
    
    top_k_indices = np.argsort(similarity_scores[0])[-40:][::-1]  # Top 6 indices with highest similarity

# Print the results (book indices and cosine similarity scores)
    for i, idx in enumerate(top_k_indices):

        print(f"{full_book_embeddings_copy.iloc[idx]['title']} | {full_book_embeddings_copy.iloc[idx]['genre_consolidated']} | {similarity_scores[0][idx]}")

    # Add similarity scores to the dataframe
    full_book_embeddings_copy['similarity'] = similarity_scores.mean(axis=0)
    print(f"Book Embeddings DF: \n{full_book_embeddings_copy.head()}\n")

    # Get Top-K Recommendations
    recommendations = full_book_embeddings_copy.sort_values(by='similarity', ascending=False).head(top_k)
    
    response_data = {
        'recommendations':  recommendations[['title', 'similarity']].to_dict(orient="records"),  # Convert DataFrame to list of dicts
        'pca_book_embeddings': pca_transformed_book_embeddings[['genre', 'PCA_book_embeddings']].to_dict(orient="records"),  # Convert DataFrame to list of dicts
        'pca_user_embedding': calculate_user_pca_embeddings(user_embedding).tolist()  # Convert NumPy array to list
    }
    #print(f"Response data: {response_data}")

    return response_data
