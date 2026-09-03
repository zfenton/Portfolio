### Import the necessary libraries
from pydantic import BaseModel, field_validator
from typing import List, Optional
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
# from datetime import datetime
from fastapi.staticfiles import StaticFiles
import requests
import json
from contextlib import asynccontextmanager

import sagemaker
import boto3


### Import the necessary functions
from src.recommend import recommend
from src.stringLookup import string_lookup

global user_id_vocab_layer
global book_title_vocab_layer
global book_genre_vocab_layer
global book_authors_vocab_layer
global encoders

@asynccontextmanager
async def lifespan_context_manager(app: FastAPI):
    
    print("Starting up!")

    s3_bucket = "w210recsys"
    
    s3 = boto3.client('s3')
    
    global user_id_vocab_layer
    global book_title_vocab_layer
    global book_genre_vocab_layer
    global book_authors_vocab_layer
    global encoders
    
    # try:
    book_authors_vocab_layer = string_lookup(s3.get_object(Bucket=s3_bucket, Key="model/recModel/modelFiles/book_authors_vocab_layer.json")['Body'].read().decode('utf-8'))
    print("Loaded book_authors_vocab_layer")
    
    book_genre_vocab_layer = string_lookup(s3.get_object(Bucket=s3_bucket, Key="model/recModel/modelFiles/book_genre_vocab_layer.json")['Body'].read().decode('utf-8'))
    print("Loaded book_genre_vocab_layer")
    
    book_title_vocab_layer = string_lookup(s3.get_object(Bucket=s3_bucket, Key="model/recModel/modelFiles/book_title_vocab_layer.json")['Body'].read().decode('utf-8'))
    print("Loaded book_title_vocab_layer")
    
    user_id_vocab_layer = string_lookup(s3.get_object(Bucket=s3_bucket, Key="model/recModel/modelFiles/user_id_vocab_layer.json")['Body'].read().decode('utf-8'))
    print("Loaded user_id_vocab_layer")
        
    # except:
        
    #     book_authors_vocab_layer = {"F. Scott Fitzgerald":1,"J.D. Salinger":2, "Harper Lee":3, "J.R.R. Tolkien":4, "J.K. Rowling":5}
    #     book_genre_vocab_layer = {"Fiction":1, "Literature":2, "Classics":3, "Fantasy":4}
    #     book_title_vocab_layer = {"The Great Gatsby":1, "The Catcher in the Rye":2, "To Kill a Mockingbird":3, "The Hobbit":4, "The Lord of the Rings":5}
    #     user_id_vocab_layer = {"1":1, "2":2, "3":3, "4":4, "5":5}
    
    encoders = {}
    
    encoders['title'] = book_title_vocab_layer
    encoders['authors'] = book_authors_vocab_layer
    encoders['categories'] = book_genre_vocab_layer
    encoders['id'] = user_id_vocab_layer
    
    #print(f"Encoders: {encoders.keys()}")
    
    yield
    

rec = FastAPI(lifespan=lifespan_context_manager)

rec.mount("/static", StaticFiles(directory="src/static"), name="static")

class UserRecommended(BaseModel):
    user: str
    
class UserRecommendedResponse(BaseModel):
    recommendations: List[str]
    
class UserLLM(BaseModel):
    user_id: int
    user_book: str
    
# define the API endpoints

@rec.post("/recommended")#, response_model=UserRecommendedResponse)
async def recommended(user): 
    """Recieve user session data that consists of:
    - User ID
    - Authors
    - Liked books
    - Disliked books
    - Liked authors
    - Disliked authors
    - Like genres
    - Dislike genres
    - Liked ratings
    - Disliked ratings
    and filter information for keeping and removing. 
    
    Return top 10 recommendations by title, author, category and similarity score as a JSON response.

    Args:
        user (json): User session data

    Returns:
        json: Top 10 recommendations by title, author, category and similarity score.
    """
    
    global encoders
    
    print(f'User: {user}\n')
    print(f'User Type: {type(user)}\n')
    # if no filter is provided, set to empty

    filter = {'keep': {'title': set(), 'author': set(), 'genre_consolidated': set()},
        'remove': {'title': set(), 'author': set(), 'genre_consolidated': set([])}}
    try:
        print(f"User Input: {user}\n")
        user_json = json.loads(json.loads(user))
        print(f"TWO JSON work!!\n")
    except:
        user_json = json.loads(user)
        print(f"One JSON Work!!\n")
      #  print(f"Error decoding JSON: {e}\n")
    print(f"User Input JSON: {user_json}\n")
    # print(type(user_json)) # Debugging
    # print(f'User JSON: {user_json}\n') # Debugging
    # print(f"User JSON Keys: {user_json['instances'][0].keys()}") # Debugging
    
    # Initialize filter_info dictionary
    filter_info = {}
    # Loop through the keys in the user_json dictionary
    for key in ['keep_title', 'keep_author', 'keep_genre_consolidated', 'remove_title', 'remove_author', 'remove_genre_consolidated']:
        
        temp = key.split("_")
        
        if len(temp) == 2:
            action, col = temp
        elif len(temp) == 3:
            action, col_1, col_2 = temp
            
            col = col_1 + "_" + col_2
        
        if action not in filter_info:
            filter_info[action] = {}
        
        vals = user_json['instances'][0][key]
        
        filter_info[action][col] = set(vals)
        
        user_json["instances"][0].pop(key)
    
    # print(f"Filter: {filter_info}")
    # print(type(user_json))
    # print(f"User Only: {user_json}")
    
    
    for key in user_json['instances'][0].keys():
        if key in ['user_id','liked_books', 'disliked_books', 'liked_genres', 'disliked_genres', 'liked_authors', 'disliked_authors']:
            vals = user_json['instances'][0][key]
            
            encoder_type = key.split('_')[1]
            
            if encoder_type == 'books':
                encoder_type = 'title'
            elif encoder_type == 'genres':
                encoder_type = 'categories'
            
            encoder = encoders[encoder_type]
            
            encoded_vals = []
            
            # print(f"Key: {key}")
            # print(f"Encoder Pair: {list(encoder.items())[0:5]}")
            
            for val in vals:
                encoded_vals.append(encoder.get(val,0)) # Returns stringlookup value or 0 if not found
                
            encoded_vals.extend([0]*(20 - len(encoded_vals)))
            
            # print(f"Encoded Values: {encoded_vals}")
                
            user_json["instances"][0][key] = encoded_vals
    
    # print("Santity Check")
    # print(f"user_json['instances'][0]['user_id']: {user_json['instances'][0]['user_id'] }\n")
    
    # Adjusting the user_id to not be in an array
    user_json["instances"][0]['user_id'] = user_json["instances"][0]['user_id'][0]

    # Adjusting the extra book info to be wrapped in lists
    user_json["instances"][0]['categories'] = [user_json["instances"][0]['categories']]
    user_json["instances"][0]['description'] = [user_json["instances"][0]['description']]
    user_json["instances"][0]['target_book'] = [user_json["instances"][0]['target_book']]
    user_json["instances"][0]['target_book_rating'] = [user_json["instances"][0]['target_book_rating']]
    
    # Adjust the lengths of the liked/disliked_ratings to be 20
    user_json["instances"][0]['liked_ratings'].extend([0]*(20 - len(user_json["instances"][0]['liked_ratings'])))
    user_json["instances"][0]['disliked_ratings'].extend([0]*(20 - len(user_json["instances"][0]['disliked_ratings'])))
    
    # print(f"Encoded User JSON: {user_json}\n")
    
    user_input = json.dumps(user_json)
    
    print(f'User Input: {user_input}\n')
    
    
    # payload = {
    #     "instances": [
    #         {
    #             "authors": 0,
    #             "user_id": 4,
    #             "liked_books": [15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "disliked_books": [55, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "liked_genres": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "disliked_genres": [50, 41, 93, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "liked_authors": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "disliked_authors": [37, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "liked_ratings": [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "disliked_ratings": [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "categories": [0],
    #             "description": [0],
    #             "target_book": [0],
    #             "target_book_rating": [0]
    #         }
    #     ]
    # }
    
    # payload = json.dumps(payload)
    
    # print(f"Payload: {payload}\n")
    
    # filter = user_json["filter"]
    # print(f'Filter: {filter}')
    #myJSON = json.dumps(user_json)
    print(f"User Profile: \n {user_input}\n")
    model_request = requests.post('https://f1bfm11ckf.execute-api.us-east-1.amazonaws.com/dev', json=user_input)

    model_return = json.loads(model_request.text)
    print(f'model_returns: {model_return}')
    model_body = json.loads(model_return["body"])
    print(f'model_body: {model_body}')
    user_embedding = model_body["result"]["predictions"][0] # Our User Embedding
    print(f"User Embedding: {user_embedding}\n")

    recommendation = recommend(user_embedding, filter_info)
    
    #print(f"Pre-recommendation: {recommendation}\n")
 
    return recommendation

@rec.get("/llm")
async def llm(user: UserLLM):
    return {"message": "User LLM recommendations retrieved successfully"}
