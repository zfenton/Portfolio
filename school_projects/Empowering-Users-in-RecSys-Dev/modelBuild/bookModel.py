import tensorflow as tf
import numpy as np
import pandas as pd
from typing import Dict, Text
from tensorflow.python.keras.layers import Embedding, StringLookup
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import Input
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers import Concatenate
from tensorflow.python.keras import Sequential


class BookModel(tf.keras.Model):
    '''
    The book(query) tower that processes book data.
    '''

    def __init__(self, book_data: pd.DataFrame, embedding_dimensions: int, text_vectorization_max_tokens: int, dense_projection_book):
        '''
        :param book_data: DataFrame containing book information.
        :param embedding_dimensions: Number of dimensions in embedding layer.
        :param text_vectorization_max_tokens: Maximum number of tokens to vector.
        '''
        super().__init__()

        # Extract unique values for embeddings
        self.feature_book_title_name = "title"
        self.feature_author_name = "authors"
        self.feature_summary_name = "description"
        self.feature_genre_name = "categories"

        unique_titles = book_data[self.feature_book_title_name].astype(str).unique()
        unique_authors = book_data[self.feature_author_name].astype(str).unique()
        unique_summaries = book_data[self.feature_summary_name].astype(str).unique()
        unique_genres = book_data[self.feature_genre_name ].astype(str).unique()

        self.dense_projection_book = dense_projection_book
        
        # Book Title embedding
        self.book_title_embedding_layers = tf.keras.layers.Embedding(input_dim=len(unique_titles) + 1, output_dim=embedding_dimensions, name='book_title_embedding')

        # Book Author embedding
        self.book_author_embedding_layers = tf.keras.layers.Embedding(input_dim=len(unique_authors) + 1, output_dim=embedding_dimensions, name='book_author_embedding')

        # Book Summaries embedding
        self.book_summaries_embedding_layers = tf.keras.layers.Embedding(input_dim=len(unique_summaries) + 1, output_dim=embedding_dimensions, name='book_summary_embedding')

        # Book Genere embedding
        self.book_genre_emdedding_layers = tf.keras.layers.Embedding(input_dim=len(unique_genres) + 1, output_dim=embedding_dimensions, name='book_genre_embedding')
    
        # print("Finsihed setting up book tower\n")

    def call(self, book_data: Dict[str, tf.Tensor]) -> tf.Tensor:
        # print("Entered book tower call\n")
    
        # tf.print(f"book_data: {book_data}")
        
        # Handle case where 'target_book' might not exist
        try:
            if len(book_data['target_book'].shape) == 0:
                book_data['target_book'] = tf.expand_dims(book_data['target_book'], axis=0)
            
            book_title_embed = self.book_title_embedding_layers(book_data['target_book'])
        except KeyError:
            if len(book_data['title'].shape) == 0:
                book_data['title'] = tf.expand_dims(book_data['title'], axis=0)
                
            book_title_embed = self.book_title_embedding_layers(book_data['title'])

        
        if len(book_data['authors'].shape) == 0:
            book_data['authors'] = tf.expand_dims(book_data['authors'], axis=0)
            book_data['description'] = tf.expand_dims(book_data['description'], axis=0)
            book_data['categories'] = tf.expand_dims(book_data['categories'], axis=0)
            
        book_author_embed = self.book_author_embedding_layers(book_data['authors'])
        book_summaries_embed = self.book_summaries_embedding_layers(book_data['description'])
        book_genre_embed = self.book_genre_emdedding_layers(book_data['categories'])

        # book_title_embed = tf.expand_dims(book_title_embed, axis=0)
        # book_author_embed = tf.expand_dims(book_author_embed, axis=0)
        # book_summaries_embed = tf.expand_dims(book_summaries_embed, axis=0)
        # book_genre_embed = tf.expand_dims(book_genre_embed, axis=0)
        
        # tf.print(f"book_title_embed.shape: {book_title_embed.shape}")
        # tf.print(f"book_author_embed.shape: {book_author_embed.shape}")
        # tf.print(f"book_summaries_embed.shape: {book_summaries_embed.shape}")
        # tf.print(f"book_genre_embed.shape: {book_genre_embed.shape}")
    
        # Concatenation without expand_dims
        concatenated_embeddings = tf.concat([
            book_title_embed,
            book_author_embed,
            book_summaries_embed,
            book_genre_embed
        ], axis=-1)  # Use last axis for feature concat
    
        # tf.print(f"concatenated_embeddings.shape: {concatenated_embeddings.shape}")
    
        # Apply projection to 64D embedding
        projected_embeddings = self.dense_projection_book(concatenated_embeddings)
    
        # tf.print(f"projected_embeddings.shape: {projected_embeddings.shape}")
    
        return projected_embeddings