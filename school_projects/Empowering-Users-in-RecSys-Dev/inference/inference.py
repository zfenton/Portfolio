import os
import pickle
import json
import numpy as np
import logging
import boto3
import pandas as pd
from flask import Flask, request, jsonify
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# Trying with out a flask app
app = Flask(__name__)

# Define the model directory
# model_dir = "model_checkpoint/model.pkl"
# book_dir = "model_checkpoint/book_embeddings.pkl"
# unique_dir = "model_checkpoint/unique_titles.pkl"

# model_dir = "./data/"
# book_dir = "./data/"
# unique_dir = "./data/"

def model_fn(model_dir):
    """
    Load the model.user_model and book_embeddings from the directory
    """
    
    model = pickle.loads(s3.Bucket("w210recsys").Object(model_dir).get()['Body'].read())
    model_path = os.path.join(model_dir, 'model.pkl')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f'Model file does not exist: {model_path}')

    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)

    logger.info("Model loaded successfully")
    return model

def book_embeddings_fn(book_dir):
    """
    Load the book embeddings
    """
    book_embeddings = pickle.loads(s3.Bucket("w210recsys").Object(book_dir).get()['Body'].read())
    # book_embeddings_path = os.path.join(model_dir, 'book_embeddings.pkl')
    # if not os.path.exists(book_embeddings_path):
    #     raise FileNotFoundError(f'Book embeddings file does not exist: {book_embeddings_path}')

    # with open(book_embeddings_path, 'rb') as book_embeddings_file:
    #     book_embeddings = pickle.load(book_embeddings_file)

    logger.info("Book embeddings loaded successfully")
    return book_embeddings

def unique_titles_fn(unique_dir):
    """
    Load the unique titles
    """
    unique_titles = pickle.loads(s3.Bucket("w210recsys").Object(unique_dir).get()['Body'].read())
    # unique_titles_path = os.path.join(model_dir, 'unique_titles.pkl')
    # if not os.path.exists(unique_titles_path):
    #     raise FileNotFoundError(f'Unique titles file does not exist: {unique_titles_path}')

    # with open(unique_titles_path, 'rb') as unique_titles_file:
    #     unique_titles = pickle.load(unique_titles_file)

    logger.info("Unique titles loaded successfully")
    return unique_titles

def input_fn(request_body, request_content_type='application/json'):
    """
    Process the input data from the request body.
    """
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        #features=np.array([input_data.get('feature1', 0), input_data.get('feature2', 0)]).reshape(1, -1)
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """
    Make user embeddings from model and input data
    """
    user_embeddings = model.predict(input_data)
    return user_embeddings

def output_fn(prediction, accept='application/json'):
    """
    Format the prediction ouput as specified
    """
    recs = []
    book_embeddings = book_embeddings_fn(book_dir)
    unique_titles = unique_titles_fn(unique_dir)
    
    user_embeddings_2d = np.expand_dims(prediction, axis=0)
    #get the cosine similarity of user embeddings and book embeddings
    cosine_sim =  cosine_similarity(user_embeddings_2d, book_embeddings)
    #from cosine_similarities, get the books for top 3 as a tuple
    top_3_indicies = np.argsort(cosine_sim[0])[::-1][:3]
    for i in top_3_indicies:
        recs.append(unique_titles[i])
    response = {'recommendations': recs}
    if accept =='application/json':
        return json.dumps(response), accept
    else:
        raise ValueError(f"Unsorpported accept type: {accept}")

model_dir = "s3://w210recsys/model_checkpoint/"
book_dir = "/model_checkpoint/book_embeddings.pkl"
unique_dir = "/model_checkpoint/unique_titles.pkl"    

model = model_fn(model_dir)
# book_embeddings = book_embeddings_fn(book_dir)
# unique_titles = unique_titles_fn(unique_dir)

@ app.get("/")
def root():
    """
    Health check endpoint to verify if the model is loaded.
    """
    health = model is not None
    status = 200 if health else 404
    return jsonify({'status': 'Healthy' if health else 'UnHealthy'}), status

@app.post('/recommendation')
def recommend():
    """
    get recommendations
    """
    data = request.data.decode('utf-8')
    content_type = request.content_type

    # Process input
    input_data = input_fn(data, content_type)

    # Get user embeddings
    embeddings = predict_fn(input_data, model)
    

    # Formatt the output
    response, content_type = output_fn(embeddings, content_type)
    return response, 200, {'Content-Type': content_type}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

