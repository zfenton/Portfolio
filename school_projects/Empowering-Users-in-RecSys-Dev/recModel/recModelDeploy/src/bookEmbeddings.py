# Load book embeddings

# Imports
import numpy as np
import sagemaker
import io
import boto3
import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def load_book_embeddings(s3_bucket, aws_book_embeddings_path, aws_books_df_path):
    """Load book embeddings and books dataframe from S3 into memory. Concat the embeddings
    onto the books dataframe and save the dataframe as a .pkl file to src/static/data.

    Args:
        s3_bucket (str): S3 bucket name (e.g. 'w210recsys) 
        aws_book_embeddings_path (str): S3 path to book embeddings (e.g. 'model/recModel/modelFiles/book_embeddings.npy')
        aws_books_df_path (str): S3 path to books dataframe (e.g. 'model/recModel/modelFiles/books_df.csv')

    Returns:
        pandas.DataFrame: dataframe with book titles and embeddings
    """
    
    s3 = boto3.client('s3')

    response = s3.get_object(Bucket=s3_bucket, Key=aws_book_embeddings_path)
    # Download the books_df file from S3 into memory
    books_df = s3.get_object(Bucket=s3_bucket, Key=aws_books_df_path)
    print("Successfully loaded objects from S3: response, books_df")
    
    # Read the data into a BytesIO buffer
    buffer = io.BytesIO(response['Body'].read())
    print(f"Loaded book_embeddings to buffer: {buffer}")
    
    books_df_ = io.BytesIO(books_df['Body'].read())
    
    print(f"Loaded books_df to buffer: {books_df_}")
    
    books_df_.seek(0)  # Move to the start of the buffer
    
    df = pd.read_pickle(books_df_)
    
    # Restict data in bookS_df to only the columns we need + unique book titles
    df = df.drop_duplicates(subset=['title'], keep='first')
    
    df['embeddings'] = [embed for embed in np.load(buffer)]

    # Load numpy array from buffer
    
    print(f"Successfully loaded book_embeddings to books_df {books_df}")
    
    # Save the books_df as a .pkl file to src/static/data
    df.to_pickle('src/static/full_book_embeddings.pkl')
    
    return df
