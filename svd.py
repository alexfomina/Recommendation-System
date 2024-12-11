import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from db import db_ops

# Use the existing db_ops singleton instance
db = db_ops()

def load_data_from_db():
    """
    Load interaction data from the database.
    """
    query = """
    SELECT UserID, CourseID, Value
    FROM UserItemInteractions
    """
    db.cursor.execute(query)
    interaction_data = db.cursor.fetchall()
    interaction_df = pd.DataFrame(interaction_data, columns=['UserID', 'CourseID', 'Value'])

    # Ensure no duplicates and pivot the table
    interaction_df = interaction_df.groupby(['UserID', 'CourseID']).agg({'Value': 'max'}).reset_index()
    interaction_matrix = interaction_df.pivot(index='UserID', columns='CourseID', values='Value').fillna(0)
    return interaction_matrix

def perform_svd(interaction_matrix, k=50):
    """
    Perform Singular Value Decomposition (SVD).
    """
    interaction_array = interaction_matrix.to_numpy()
    k = min(k, interaction_array.shape[0] - 1, interaction_array.shape[1] - 1)
    U, sigma, Vt = svds(interaction_array, k=k)
    sigma = np.diag(sigma)
    predicted_ratings = np.dot(np.dot(U, sigma), Vt)

    predicted_ratings_df = pd.DataFrame(
        predicted_ratings, index=interaction_matrix.index, columns=interaction_matrix.columns
    )
    return predicted_ratings_df

def save_recommendations_to_db(predicted_ratings_df):
    """
    Save predicted ratings to the Recommendations table in the database.
    """
    recommendations = predicted_ratings_df.reset_index().melt(
        id_vars="UserID", var_name="CourseID", value_name="PredictedRating"
    )

    query = """
    INSERT INTO Recommendations (UserID, CourseID, PredictedRating)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE PredictedRating = VALUES(PredictedRating)
    """
    for _, row in recommendations.iterrows():
        db.cursor.execute(query, (row['UserID'], row['CourseID'], row['PredictedRating']))
    db.connection.commit()

def generate_recommendations():
    """
    Main function to generate and save recommendations.
    """
    print("Loading data from database...")
    interaction_matrix = load_data_from_db()
    print("Performing SVD...")
    predicted_ratings_df = perform_svd(interaction_matrix)
    print("Saving recommendations to database...")
    save_recommendations_to_db(predicted_ratings_df)
    print("Recommendations successfully generated and saved.")

if __name__ == "__main__":
    generate_recommendations()
