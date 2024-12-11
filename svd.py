import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
import sqlite3

# Load interaction data from the database
def load_data_from_db():
    conn = sqlite3.connect("database.db")
    query = """
    SELECT UserID, CourseID, Value
    FROM UserItemInteractions
    """
    interaction_df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Ensure no duplicates and pivot the table
    interaction_df = interaction_df.groupby(['UserID', 'CourseID']).agg({'Value': 'max'}).reset_index()
    interaction_matrix = interaction_df.pivot(index='UserID', columns='CourseID', values='Value').fillna(0)
    return interaction_matrix

# Perform Singular Value Decomposition
def perform_svd(interaction_matrix, k=50):
    # Convert the interaction matrix to a numpy array
    interaction_array = interaction_matrix.to_numpy()
    
    # Adjust the number of latent features if necessary
    k = min(k, interaction_array.shape[0] - 1, interaction_array.shape[1] - 1)
    
    # Perform SVD
    U, sigma, Vt = svds(interaction_array, k=k)
    sigma = np.diag(sigma)  # Convert sigma to a diagonal matrix
    
    # Predict ratings by reconstructing the matrix
    predicted_ratings = np.dot(np.dot(U, sigma), Vt)
    
    # Convert the predicted ratings back to a DataFrame
    predicted_ratings_df = pd.DataFrame(
        predicted_ratings, index=interaction_matrix.index, columns=interaction_matrix.columns
    )
    return predicted_ratings_df

# Save recommendations to the database
def save_recommendations_to_db(predicted_ratings_df):
    conn = sqlite3.connect("database.db")
    
    # Prepare the data for saving
    recommendations_df = predicted_ratings_df.reset_index().melt(
        id_vars="UserID", var_name="CourseID", value_name="PredictedRating"
    )
    
    # Save to database
    recommendations_df.to_sql("Recommendations", conn, if_exists="replace", index=False)
    conn.close()

# Main execution
if __name__ == "__main__":
    # Load and prepare data from the database
    interaction_matrix = load_data_from_db()
    
    # Perform SVD and generate predictions
    predicted_ratings_df = perform_svd(interaction_matrix)
    
    # Save the recommendations
    save_recommendations_to_db(predicted_ratings_df)
    print("Recommendations have been successfully generated and saved to the database.")
