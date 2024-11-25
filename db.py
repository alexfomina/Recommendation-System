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
                                                                password = 'HenryCPSC408', #CPSC408!
                                                                auth_plugin = 'mysql_native_password',
                                                                database = 'RecommendationApp')
            cls._instance.cursor = cls._instance.connection.cursor()
            print("Database connection established")
        return cls._instance
    
    def create_tables(self):

        query = '''
            CREATE TABLE UserInterests (
            UserInterestID PK VARCHAR(60),
            UserID FK VARCHAR(60),
            TopicID FK VARCHAR(60),
            InterestLevel INT
            );
            '''
        #TODO: Change interestLevel in ER diagram from varchar to INT
        #TODO: Not sure if 'number' and 'string' are even a datatypes in ones below
        #TODO: Also PK and FK should maybe be changed to INT or we can change up how keys are generated
        self.cursor.execute(query)
        self.connection.commit()
        print("Created User Interests table")
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
    
    #TODO: Test if this works
    #edit different values of a user account
    def edit_account(self, userID, field_to_edit, new_value):
        #TODO: Email can be an option here but need to add it to User table
        '''
        Parameter options

        field_to_edit - (Name, Profile)
        '''
        
        valid_fields = ["Name", "Profile"]

        if field_to_edit not in valid_fields:
            raise ValueError(f"Can not edit field: {field_to_edit}")

        #update User table based on which field should be updated
        #use username and password to find user to update
        query = f'''
            UPDATE User
            SET {field_to_edit} = %s
            WHERE UserID = %s;
            '''
        #TODO: test this to see if f string is allowed while still using %s for fields
        
        self.cursor.execute(query, (new_value, userID))
        self.connection.commit()

    #TODO: Test if this works
    #set user interest
    def set_user_interest(self, userID, topic, interest_level):
        
        #generate random id
        id = uuid.uuid4().int & (1 << 16) - 1

        #get topicID from Topic table
        topicID = db_ops.get_topicID(topic)

        query = '''
            INSERT INTO UserInterests
            VALUES (%s,%s,%s,%s);
            '''
        
        self.cursor.execute(query, (id, userID, topicID, interest_level))
        self.connection.commit()

    #function to get userID
    def get_userID(self, username,password):
        '''
        Helper function that returns the userID given a username and password
        '''

        query = '''
            SELECT UserID
            FROM User
            WHERE Username = %s AND Password = %s;
            '''
        
        self.cursor.execute(query, (username, password))
        
        #get result
        userID = self.cursor.fetchone

        return userID
    
    #function to get topicID
    def get_topicID(self, topicName):
        '''
        Helper function that returns topicID given topicName
        '''

        query = '''
            SELECT TopicID
            FROM Topic
            WHERE topicName = %s;
            '''
        
        self.cursor.execute(query, topicName)
        
        #get result
        topicID = self.cursor.fetchone()

        return topicID
    
    #Returns a history of viewed, enrolled, or completed courses 
    #(Note: when storing values in InteractionType they must be stored as viewed, enrolled, completed)
    def course_interaction_history(self, userID, interaction_type):
        '''
        Access interaction history

        Parameter requirements:
        interaction_type - (viewed, enrolled, completed)

        Returns a list of tuples - (Course name, timestamp, rating) for each course
        '''

        valid_fields = ['viewed', 'enrolled', 'completed']

        if interaction_type not in valid_fields:
            raise ValueError(f"Non valid interaction type: {interaction_type}")

        #selects the course names based on courseID as well as timestamp and rating of courses users have interacted with in a specific way
        query = '''
            SELECT (SELECT CourseName FROM Course WHERE Course.CourseID = UserItemInteraction.CourseID) AS CourseName, 
            Timestamp, Rating
            FROM UserItemInteraction
            WHERE UserID = %s AND InteractionType = %s;
            '''
        
        self.cursor.execute(query, (userID, interaction_type))

        results = self.cursor.fetchall()

        return results


    #Find courses by keywords, topic, or category.
    
    #find courses from keywords
    def search_course_keyword(self, search):
        
        #searches for any courses containing the keyword
        query = '''
            SELECT CourseName
            FROM Course
            WHERE CourseName LIKE CONCAT('%', %s, '%');
            '''
        
        self.cursor.execute(query, search)
        
        results = self.cursor.fetchall()

        #turn results from a list of tuples into just a list
        list_results = [row[0] for row in results]

        return list_results
    
    #find courses from category
    def search_course_category(self, search):
        #searches for any course category containing the keyword
        query = '''
            SELECT CourseName
            FROM Course
            WHERE Category LIKE CONCAT('%', %s, '%');
            '''
        
        self.cursor.execute(query, search)
        
        results = self.cursor.fetchall()

        #turn results from a list of tuples into just a list
        list_results = [row[0] for row in results]

        return list_results
    
    #find course from topic
    def search_course_topic(self, search):
        
        #Selects courses that have a topic that includes part of the keyword
        query = '''
            SELECT DISTINCT CourseName
            FROM Course
            JOIN CourseTopic USING (CourseID)
            JOIN Topic USING (TopicID)
            WHERE TopicName LIKE CONCAT('%', %s, '%');
            '''
        
        self.cursor.execute(query, search)
        
        results = self.cursor.fetchall()

        #turn results from a list of tuples into just a list
        list_results = [row[0] for row in results]

        return list_results
#test
# 1. User Profile and Preferences Management
# Register/Login: Create an account(DONE) or log in with existing credentials.
# Edit Profile: Update personal details (e.g., name, email).(DONE)
# Set Interests: Select topics of interest to enhance recommendations.(DONE)
# View Learning History: Access a history of viewed, enrolled, or completed courses.(DONE)
# 2. Course Exploration and Search
# Search Courses: Find courses by keywords, topics, or categories.(DONE)
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

