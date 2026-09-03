import tensorflow as tf
import tensorflow_recommenders as tfrs
import tensorflor.keras.layers as layers
from typing import Dict
import time

import boto3
import io
import os
import sagemaker
import pandas as pd
import numpy as np

from userModel import UserModel
from bookModel import BookModel


class BooksTwoTowersModel(tfrs.Model):
    def __init__(self, user_data: pd.DataFrame, book_metadata: pd.DataFrame, embedding_dimensions=64):
        super().__init__()

        self.dense_projection_user = tf.keras.layers.Dense(64, name='user_dense_projection')
        self.dense_projection_book = tf.keras.layers.Dense(64, name='book_dense_projection')

        self.user_model = UserModel(user_data, book_metadata, self.dense_projection_user, embedding_dimensions)

        self.book_model = BookModel(book_metadata, embedding_dimensions, 10000, self.dense_projection_book)

        self.candidate_ds = tf.data.Dataset.from_tensor_slices({
            'title': tf.convert_to_tensor(book_metadata['title'].values, dtype=tf.int64),
            'authors': tf.convert_to_tensor(book_metadata['authors'].values, dtype=tf.int64),
            'description': tf.convert_to_tensor(book_metadata['description'].values, dtype=tf.int64),
            'categories': tf.convert_to_tensor(book_metadata['categories'].values, dtype=tf.int64)
        })

        candidates = self.candidate_ds.batch(1).map(
            lambda x: self.book_model(x), num_parallel_calls=tf.data.AUTOTUNE
        ).map(
            lambda x: tf.squeeze(x, axis=0)
        )

        self.task = tfrs.tasks.Retrieval(
            metrics=tfrs.metrics.FactorizedTopK(
                candidates=candidates.batch(1),
                ks=(10, 20, 50)
            )
        )

        self.full_book_embeddings = None
        self.full_book_embeddings_copy = None

    def compute_loss(self, features: Dict[str, tf.Tensor], training=False) -> tf.Tensor:

        user_embeddings = self.user_model(features)

        target_book_embeddings = self.book_model(features)

        retrieval_loss = self.task(user_embeddings, target_book_embeddings, compute_metrics=not training)

        return retrieval_loss

    def load_book_embeddings(self, path, books_df):

        # We want to load in books' embeddings to make sure our model has them on hand to give direct recommendations
        # Load in via boto3 and sagemaker

        role = sagemaker.get_execution_role()
        sm_session = sagemaker.Session()
        bucket_name = sm_session.default_bucket()
        s3 = boto3.client('s3')

        # Download the file from S3 into memory
        response = s3.get_object(Bucket=bucket_name, Key=path)

        # Read the data into a BytesIO buffer
        buffer = io.BytesIO(response['Body'].read())

        # Load numpy array from buffer
        books_df['embeddings'] = [embed for embed in np.load(buffer)]

        self.full_book_embeddings = books_df
        
        print(self.full_book_embeddings)
    
    def recommend(self, session_info, filter, top_k=10, path='embeddings/book_embeddings.npy'):
        """
        Recommend top_k books based on cosine similarity using book embeddings.
        :param filter: Dictionary with 'keep' and 'remove' filters.
        :param input_book_title: Title of the book to find recommendations for.
        :param top_k: Number of recommendations to return.
        :param path: Path to embeddings if they need to be loaded.
        :return: DataFrame with top_k recommendations.
        """
        from sklearn.metrics.pairwise import cosine_similarity

        # Ensure that embeddings are loaded
        if self.full_book_embeddings is None:
            self.load_book_embeddings(path, self.full_book_embeddings_copy)

        # Apply filtering logic
        self.full_book_embeddings_copy = self.full_book_embeddings.copy()
        
        # Apply 'keep' filters
        for key, value_set in filter.get('keep', {}).items():
            if value_set:
                self.full_book_embeddings_copy = self.full_book_embeddings_copy[
                    self.full_book_embeddings_copy[key].isin(value_set)]
        
        # Apply 'remove' filters
        for key, value_set in filter.get('remove', {}).items():
            if value_set:
                self.full_book_embeddings_copy = self.full_book_embeddings_copy[
                    ~self.full_book_embeddings_copy[key].isin(value_set)]

        # Get user embeddings
        user_embeddings = self.user_model(session_info)
        
        # Get book embeddings (make sure to extract relevant embeddings)
        book_embeddings = np.vstack(self.full_book_embeddings_copy['embeddings'].values)

        # Compute Cosine Similarity between user and book embeddings
        similarity_scores = cosine_similarity(user_embeddings, book_embeddings)

        # Add similarity scores to the dataframe
        self.full_book_embeddings_copy['similarity'] = similarity_scores.mean(axis=0)

        # Get Top-K Recommendations
        recommendations = self.full_book_embeddings_copy.sort_values(by='similarity', ascending=False).head(top_k)

        return recommendations[['title', 'authors', 'categories', 'similarity']]
    
