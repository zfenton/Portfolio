from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import pickle as pk

def calculate_pca_embeddings(books_df_unique):
    
    #print(books_df_unique.head())
    
    avg_genre_emb_df = pd.DataFrame(columns=["genre", "avg_embedding"])

    for i, genre in enumerate(books_df_unique['genre_consolidated'].unique()):
        
        #print(i, genre)

        embedding_matrix = np.array(books_df_unique[books_df_unique['genre_consolidated'] == genre]['embeddings'].tolist())

        average_embedding = embedding_matrix.mean(axis=0)

        avg_genre_emb_df.loc[i] = [genre, average_embedding]
        

    # avg_genre_emb_df["avg_embedding"] = avg_genre_emb_df["avg_embedding"].apply(lambda x: np.array(eval(x)) if isinstance(x, str) else np.array(x))

    X = np.vstack(avg_genre_emb_df["avg_embedding"].values)

    pca = PCA(n_components=3)
    X_pca = pca.fit_transform(X)
    
    # Convert the PCA transformed data to a DataFrame

    df_pca = pd.DataFrame({"PCA_book_embeddings": [row.tolist() for row in X_pca]})
    
    df_pca["genre"] = avg_genre_emb_df["genre"]
    
    # Save the PCA model as a pickel file
    with open('src/static/pca_model.pkl', 'wb') as file:
        pk.dump(pca, file)
        
    df_pca.to_pickle('src/static/pca_transformed_book_embeddings.pkl')
    
    return df_pca

def calculate_user_pca_embeddings(user_embedding):
    # Load the PCA model from the pickle file
    with open('src/static/pca_model.pkl', 'rb') as file:
        pca = pk.load(file)
    
    user_embedding = np.array(user_embedding).reshape(1, -1)
    user_embedding_pca = pca.transform(user_embedding)
    
    return user_embedding_pca