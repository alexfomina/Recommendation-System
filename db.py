from datetime import datetime
import uuid
import mysql.connector

class db_ops:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            # Initialize database connection here
            cls._instance.connection = mysql.connector.connect(host = 'localhost',
                                                                user = 'root',
                                                                password = 'CPSC408!',
                                                                auth_plugin = 'mysql_native_password',
                                                                database = 'RecommendationApp')
            cls._instance.cursor = cls._instance.connection.cursor()
            print("Database connection established")
        return cls._instance
    
    def create_tables(self):

        query = '''
            CREATE TABLE Topic (
            TopicID VARCHAR(60) PRIMARY KEY,
            TopicName VARCHAR(60)
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created Topic table")

        query = '''
            CREATE TABLE Course (
            CourseID VARCHAR(60) PRIMARY KEY,
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
            UserID VARCHAR(60) PRIMARY KEY,
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
        CREATE TABLE UserInterests (
        UserInterestID VARCHAR(60) PRIMARY KEY ,
        FOREIGN KEY (UserID) REFERENCES USER(UserID),
        FOREIGN KEY (TopicID) REFERENCES VARCHAR(60),
        InterestLevel VARCHAR(60)
        );
        '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created User Interests table")


        query = '''
            CREATE TABLE Recommendation (
            RecommendationID string PRIMARY KEY ,
            FOREIGN KEY (UserID) REFERENCES USER(UserID),
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID),
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
            FOREIGN KEY (UserID) REFERENCES USER(UserID)
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID)
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
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID),
            FOREIGN KEY (TopicID) REFERENCES TOPIC(TopicID)
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created CourseTopic table")
    #TODO- test if this works
    """
        Function to initialize user account
    """
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
    #TODO- test if this works
    """
        Function to check if a user account already exists
    """
    def check_user_account(self, username, password):
        # Choose the appropriate table based on user_type
        query = '''
            SELECT EXISTS (SELECT 1 FROM USER WHERE username = %s AND password = %s);
            '''
        print("made it past query")
        # Execute the query with parameters to check if the user exists
        self.cursor.execute(query, (username, password))
        
        # Fetch the result
        result = self.cursor.fetchone()

        # Return True if user exists (1) or False if not (0)
        print(result[0])
        self.connection.commit()
        return result[0] == 1
    
    def get_user_details(self, username):
        query = "SELECT Username, Name, Profile, DateCreated FROM User WHERE Username = %s"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        if result:
            return {
                "Username": result[0],
                "Name": result[1],
                "Profile": result[2],
                "DateCreated": result[3].strftime("%Y-%m-%d %H:%M:%S")
            }
        return None
    def delete(self):
        query = '''DROP DATABASE RECOMMENDATIONAPP;'''
        self.cursor.execute(query)
        self.connection.commit()
    #def edit_account(self, param, username, password):
        
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

