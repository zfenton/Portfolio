# Build, Compile, Train and save two towers model

import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from typing import Dict, Text
from tensorflow.python.keras.layers import Embedding, StringLookup
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import Input
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers import Concatenate
from tensorflow.python.keras import Sequential
from modelBuild.userModel import UserModel
from modelBuild.bookModel import BookModel  

def build_model(user_data: pd.DataFrame, book_metadata: pd.DataFrame, dense_projection_user, dense_projection_book, embedding_dimensions=64):
    # Build user tower
    user_tower = UserModel(user_data, book_metadata, dense_projection_user, embedding_dimensions)

    # Build book tower
    book_tower = BookModel(user_data, book_metadata, dense_projection_book, embedding_dimensions)

    # Build the model
    user_input = Input(shape=(1,), name='user_id')
    liked_books_input = Input(shape=(1,), name='liked_books')
    disliked_books_input = Input(shape=(1,), name='disliked_books')
    liked_genres_input = Input(shape=(1,), name='liked_genres')
    disliked_genres_input = Input(shape=(1,), name='disliked_genres')
    liked_authors_input = Input(shape=(1,), name='liked_authors')
    disliked_authors_input = Input(shape=(1,), name='disliked_authors')

    book_title_input = Input(shape=(1,), name='book_title')
    book_genre_input = Input(shape=(1,), name='book_genre')
    book_author_input = Input(shape=(1,), name='book_author')

    user_embedding = user_tower({'user_id': user_input, 'liked_books': liked_books_input, 'disliked_books': disliked_books_input, 'liked_genres': liked_genres_input, 'disliked_genres': disliked_genres_input, 'liked_authors': liked_authors_input, 'disliked_authors': disliked_authors_input})
    book_embedding = book_tower({'book_title': book_title_input, 'book_genre': book_genre_input, 'book_author': book_author_input})

    # Concatenate the embeddings
    concatenated = Concatenate()([user_embedding, book_embedding])

    # Dense layer
    dense = Dense(64, activation='relu')(concatenated)

    # Output layer
    output = Dense(1, activation='sigmoid')(dense)

    # Build the model
    model = Model(inputs=[user_input, liked_books_input, disliked_books_input, liked_genres_input, disliked_genres_input, liked_authors_input, disliked_authors_input, book_title_input, book_genre_input, book_author_input], outputs=output)

    return model

def compile_model(model):
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_model(model, user_data: pd.DataFrame, book_metadata: pd.DataFrame, epochs=5):
    # Prepare the data
    user_ids = user_data['user_id'].astype(str).tolist()
    liked_books = user_data['liked_books'].astype(str).tolist()
    disliked_books = user_data['disliked_books'].astype(str).tolist()
    liked_genres = user_data['liked_genres'].astype(str).tolist()
    disliked_genres = user_data['disliked_genres'].astype(str).tolist()
    liked_authors = user_data['liked_authors'].astype(str).tolist()
    disliked_authors = user_data['disliked_authors'].astype(str).tolist()

    book_titles = book_metadata['title'].astype(str).tolist()
    book_genres = book_metadata['categories'].astype(str).tolist()
    book_authors = book_metadata['authors'].astype(str).tolist()

    labels = user_data['label'].astype(int).tolist()

    # Fit the model
    model.fit([user_ids, liked_books, disliked_books, liked_genres, disliked_genres, liked_authors, disliked_authors, book_titles, book_genres, book_authors], labels, epochs=epochs)

    return model

def save_model(model, model_dir: Text):
    model.save(model_dir)
    
    return model

def main(user_data: pd.DataFrame, book_metadata: pd.DataFrame, dense_projection_user, dense_projection_book, model_dir: Text):
    model = build_model(user_data, book_metadata, dense_projection_user, dense_projection_book)
    model = compile_model(model)
    model = train_model(model, user_data, book_metadata)
    model = save_model(model, model_dir)
    
    return model

if __name__ == '__main__':
    user_data = pd.read_csv(sys.argv[1])
    book_metadata = pd.read_csv(sys.argv[2])
    dense_projection_user = sys.argv[3]
    dense_projection_book = sys.argv[4]
    model_dir = sys.argv[5]
    
    main(user_data, book_metadata, dense_projection_user, dense_projection_book, model_dir)

