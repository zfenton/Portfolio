# User/Query Model
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

class UserModel(tf.keras.Model):
    def __init__(self, user_data: pd.DataFrame, book_metadata: pd.DataFrame, dense_projection_user, embedding_dimensions=64):
        super().__init__()

        # Extract unique values from user and book metadata
        unique_user_ids = user_data['user_id'].astype(str).unique().tolist()
        unique_book_titles = book_metadata['title'].astype(str).unique().tolist()
        unique_genres = book_metadata['categories'].astype(str).unique().tolist()
        unique_authors = book_metadata['authors'].astype(str).unique().tolist()

        self.dense_projection_user = dense_projection_user
        
        # User embedding
        self.user_embedding_layers = tf.keras.layers.Embedding(input_dim=len(unique_user_ids) + 1, output_dim=embedding_dimensions, name='user_id_embedding')

        # Book embedding
        self.book_title_embedding_layers = tf.keras.layers.Embedding(input_dim=len(unique_book_titles) + 1, output_dim=embedding_dimensions, name='book_embedding')

        # Genre embedding
        self.genre_embedding_layers = tf.keras.layers.Embedding(input_dim=len(unique_genres) + 1, output_dim=embedding_dimensions, name='genre_embedding')

        # Author embedding
        self.author_embedding_layers = tf.keras.layers.Embedding(input_dim=len(unique_authors) + 1, output_dim=embedding_dimensions, name='author_embedding')
        
        # print("Finsihed setting up user tower\n")
    
    def call(self, inputs):
        # print("Entered User Tower Call\n")

        # This check is for adjusting the dimensions during inference when we will only pass in one item at a time to have the same dimensions
        
        if len(inputs['user_id'].shape) == 0:
            inputs['user_id'] = tf.expand_dims(inputs['user_id'], axis=0)
            inputs['liked_books'] = tf.expand_dims(inputs['liked_books'], axis=0)
            inputs['disliked_books'] = tf.expand_dims(inputs['disliked_books'], axis=0)
            inputs['liked_genres'] = tf.expand_dims(inputs['liked_genres'], axis=0)
            inputs['disliked_genres'] = tf.expand_dims(inputs['disliked_genres'], axis=0)
            inputs['liked_authors'] = tf.expand_dims(inputs['liked_authors'], axis=0)
            inputs['disliked_authors'] = tf.expand_dims(inputs['disliked_authors'], axis=0)

        # tf.print(f"inputs['user_id'].shape: {inputs['user_id'].shape}\n")
        # tf.print(f"len(inputs['user_id'].shape): {len(inputs['user_id'].shape)}\n")
        
        user_embed = self.user_embedding_layers(inputs['user_id'])
        # user_embed = tf.expand_dims(user_embed, axis=0)
        # tf.print(f"user_embed:\n{user_embed}")
        # print(f"user_id embedding shape: {user_embed.shape}")
        # print("user_id processed\n")

        def pool_embeddings(embedding_layer, input_list, weights, embedding_dim=64, pad_value=0):
            # Get embeddings
            embeddings = embedding_layer(input_list)
        
            # Create mask
            mask = tf.not_equal(input_list, pad_value)
            mask = tf.expand_dims(mask, axis=-1)
        
            # Zero out padded embeddings
            embeddings = tf.where(mask, embeddings, tf.zeros_like(embeddings))
        
            # Normalize weights (zero-safe)
            weight_sum = tf.reduce_sum(weights, axis=-1, keepdims=True)
            weight_sum = tf.where(weight_sum == 0, tf.ones_like(weight_sum), weight_sum)
            weights = weights / weight_sum
            
            # Expand weights dims
            expanded_weights = tf.expand_dims(weights, axis=-1)

            # tf.print(f"expanded_weights: {expanded_weights}")
            
            # Weighted Embeddings
            weighted_embeddings = embeddings * expanded_weights
        
            # Sum + Pool
            summed_embeddings = tf.reduce_sum(weighted_embeddings, axis=1)
            valid_counts = tf.reduce_sum(tf.cast(mask, tf.float32), axis=1)
            valid_counts = tf.where(valid_counts == 0, tf.ones_like(valid_counts), valid_counts)
            pooled_embeddings = summed_embeddings / valid_counts
        
            # Fix NaNs
            pooled_embeddings = tf.where(tf.math.is_nan(pooled_embeddings), tf.zeros_like(pooled_embeddings), pooled_embeddings)
        
            return pooled_embeddings


        
        # Process liked books
        # tf.print(f"inputs['liked_books']: {inputs['liked_books']}")
        liked_books_embed = pool_embeddings(self.book_title_embedding_layers, inputs['liked_books'], inputs['liked_ratings'])
        # tf.print(f"liked_books_embed:\n{liked_books_embed}")
        # print(f"liked books embedding shape: {liked_books_embed.shape}")
        # print("liked books processed\n")

        # Process disliked books
        # tf.print(f"inputs['disliked_books']: {inputs['disliked_books']}")
        disliked_books_embed = pool_embeddings(self.book_title_embedding_layers, inputs['disliked_books'], inputs['disliked_ratings'])
        # tf.print(f"disliked_books_embed:\n{disliked_books_embed}")
        # print(f"disliked books embedding shape: {disliked_books_embed.shape}")
        # print("disliked books processed\n")

        # Process liked genres
        # tf.print(f"inputs['liked_genres']: {inputs['liked_genres']}")
        liked_genres_embed = pool_embeddings(self.genre_embedding_layers, inputs['liked_genres'], inputs['liked_ratings'])
        # tf.print(f"liked_genres_embed:\n{liked_genres_embed}")
        # print(f"liked genres embedding shape: {liked_genres_embed.shape}")
        # print("liked genres processed\n")

        # Process disliked genres
        # tf.print(f"inputs['disliked_genres']: {inputs['disliked_genres']}")
        disliked_genres_embed = pool_embeddings(self.genre_embedding_layers, inputs['disliked_genres'], inputs['disliked_ratings'])
        # tf.print(f"disliked_genres_embed:\n{disliked_genres_embed}")
        # print(f"disliked genres embedding shape: {disliked_genres_embed.shape}")
        # print("disliked genres processed\n")

        # Process liked authors
        # tf.print(f"inputs['liked_authors']: {inputs['liked_authors']}")
        liked_authors_embed = pool_embeddings(self.author_embedding_layers, inputs['liked_authors'], inputs['liked_ratings'])
        # tf.print(f"liked_authors_embed:\n{liked_authors_embed}")
        # print(f"liked authors embedding shape: {liked_authors_embed.shape}")
        # print("liked authors processed\n")

        # Process disliked authors
        # tf.print(f"inputs['disliked_authors']: {inputs['disliked_authors']}")
        disliked_authors_embed = pool_embeddings(self.author_embedding_layers, inputs['disliked_authors'], inputs['disliked_ratings'])
        # tf.print(f"disliked_authors_embed:\n{disliked_authors_embed}")
        # print(f"disliked authors embedding shape: {disliked_authors_embed.shape}")
        # print("disliked authors processed\n")

        # Concatenate everything into a single user representation
        concatenated_embeddings = tf.concat([
            user_embed,
            liked_books_embed,
            disliked_books_embed,
            liked_genres_embed,
            disliked_genres_embed,
            liked_authors_embed,
            disliked_authors_embed
        ], axis=1)

        projected_embeddings = self.dense_projection_user(concatenated_embeddings)

        # print(f"projected_embeddings.shape: {projected_embeddings.shape}\n")
        
        return projected_embeddings