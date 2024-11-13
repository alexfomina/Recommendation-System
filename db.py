from datetime import datetime
import uuid
import mysql.connector

class db_ops():

    def __init__(self):
        self.connection = mysql.connector.connect(host = 'localhost',
                                                user = 'root',
                                                password = 'CPSC408!',
                                                auth_plugin = 'mysql_native_password',
                                                database = 'RecommendationApp')
        #Cursor object to interact with database
        self.cursor = self.connection.cursor()

        print("Connection made")
    
    def create_tables(self):

        query = '''
        CREATE TABLE UserInterests (
        UserInterestID PK VARCHAR(60),
        UserID FK VARCHAR(60),
        TopicID FK VARCHAR(60),
        InterestLevel VARCHAR(60)
        );
        '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created User Interests table")
        query = '''
            CREATE TABLE Topic (
            TopicID PK VARCHAR(60),
            TopicName VARCHAR(60)
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created User Topic table")

        query = '''
            CREATE TABLE Course (
            CourseID PK VARCHAR(60),
            CourseName VARCHAR(60),
            Description VARCHAR(60),
            Category VARCHAR(60),
            Instructor VARCHAR(60),
            AverageRating FLOAT
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created Course table")

        query = ''' 
            CREATE TABLE User (
            UserID PK VARCHAR(60),
            Username VARCHAR(60),
            Password VARCHAR(60),
            Name VARCHAR(60),
            Profile VARCHAR(60),
            DateCreated datetime
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created User table")

        query = '''
            CREATE TABLE Recommendation (
            RecommendationID PK string,
            UserID FK string,
            RecommendedCourseID FK string,
            RecommendationScore number,
            RecommendationDate date,
            Rank number
            ); 
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created Recommendation table")

        query = '''
            CREATE TABLE UserItemInteraction (
            UserID FK string,
            CourseID FK string,
            InteractionType string,
            Timestamp datetime,
            Rating number
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created UserItemInteraction table")

        query = '''
            CREATE TABLE CourseTopic (
            CourseID FK string,
            TopicID FK string
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created CourseTopic table")

    def create_user_account(self, username, password, name, profile):
           #generate random id
        id = uuid.uuid4().int & (1 << 16) - 1

        query = '''
        INSERT INTO user
        VALUES (%s, %s, %s, %s, %s)
        '''
        params = (id, username, password, name, profile)

        self.cursor.execute(query, params)
        self.connection.commit()
        print("Created account")

# 1. User Profile and Preferences Management
# Register/Login: Create an account or log in with existing credentials.
# Edit Profile: Update personal details (e.g., name, email).
# Set Interests: Select topics of interest to enhance recommendations.
# View Learning History: Access a history of viewed, enrolled, or completed courses.
# 2. Course Exploration and Search
# Search Courses: Find courses by keywords, topics, or categories.
# Filter and Sort Courses: Filter courses by topic, rating, difficulty level, popularity, or duration.
# View Course Details: Access course information, including description, topics covered, rating, and reviews.
# Browse Recommended Courses: View courses recommended by the system based on user interests and past interactions.
# 3. User-Course Interactions
# Enroll in Course: Sign up for a course to access its content.
# Rate a Course: Leave a rating and/or review after completing or viewing a course, contributing to personalized recommendations.
# Add Course to Favorites: Bookmark courses for quick access.
# View Course Progress: Track progress through enrolled courses (if applicable).
# Complete Course: Mark a course as completed, which can also trigger new or refined recommendations.
# 4. Recommendation System Interactions
# Receive Personalized Recommendations: Access recommendations based on user profile, interests, and interactions with courses.
# Rate/Interact with Recommendations: Engage with recommended courses to further refine the system’s accuracy.
# View Similar Users’ Courses: Access courses taken by users with similar interests (collaborative filtering).
# 5. User Feedback and System Improvement
# Provide Feedback: Submit feedback on course recommendations to improve future suggestions.
# Adjust Interests Based on Course Ratings: Allow users to confirm or adjust interests after rating courses highly, further refining their profile.

