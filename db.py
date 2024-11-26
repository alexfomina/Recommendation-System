from datetime import datetime
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

        #TODO: Update ER diagram data types
        query = '''
            CREATE TABLE Topic (
            TopicID INT PRIMARY KEY UNIQUE NOT NULL AUTO_INCREMENT,
            TopicName VARCHAR(60)
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created Topic table")

        query = '''
            CREATE TABLE Course (
            CourseID INT PRIMARY KEY UNIQUE NOT NULL AUTO_INCREMENT,
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
            UserID INT PRIMARY KEY UNIQUE NOT NULL AUTO_INCREMENT,
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
            UserInterestID INT PRIMARY KEY UNIQUE NOT NULL AUTO_INCREMENT,
            InterestLevel INT,
            UserID INT,
            TopicID INT,
            FOREIGN KEY (UserID) REFERENCES User(UserID),
            FOREIGN KEY (TopicID) REFERENCES Topic(TopicID)
            );
            '''
        
        self.cursor.execute(query)
        self.connection.commit()
        print("Created User Interests table")

        query = '''
            CREATE TABLE Recommendation (
            RecommendationID INT PRIMARY KEY UNIQUE NOT NULL AUTO_INCREMENT,
            RecommendationScore INT,
            RecommendationDate DATE,
            Ranking INT,
            UserID INT,
            CourseID INT,
            FOREIGN KEY (UserID) REFERENCES USER(UserID),
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID)
            ); 
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created Recommendation table")

        query = '''
            CREATE TABLE UserItemInteraction (
            InteractionType VARCHAR(20),
            Timestamp DATETIME,
            Rating INT,
            UserID INT,
            CourseID INT,
            PRIMARY KEY (UserID, CourseID),
            FOREIGN KEY (UserID) REFERENCES User(UserID),
            FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created UserItemInteraction table")

        query = '''
            CREATE TABLE CourseTopic (
            CourseID INT,
            TopicID INT,
            PRIMARY KEY (CourseID, TopicID),
            FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
            FOREIGN KEY (TopicID) REFERENCES Topic(TopicID)
            );
            '''
        self.cursor.execute(query)
        self.connection.commit()
        print("Created CourseTopic table")

    
    def delete_everything(self):
        query = '''DROP DATABASE RecommendationApp;'''
        self.cursor.execute(query)

    #TODO- test if this works
    """
        Function to initialize user account
    """
    def create_user_account(self, username, password, name, profile):

        query = '''
        INSERT INTO User (username, password, name, profile)
        VALUES (%s, %s, %s, %s)
        '''
        params = (username, password, name, profile)

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

        #get topicID from Topic table
        topicID = db_ops.get_topicID(topic)

        query = '''
            INSERT INTO UserInterests (userID, topicID, interest_level)
            VALUES (%s,%s,%s);
            '''
        
        self.cursor.execute(query, (userID, topicID, interest_level))
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
        
        self.cursor.execute(query, (topicName,))
        
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
            SELECT CourseID
            FROM Course
            WHERE CourseName LIKE CONCAT('%', %s, '%');
            '''
        
        self.cursor.execute(query, (search,))
        
        results = self.cursor.fetchall()

        #turn results from a list of tuples into just a list
        list_results = [row[0] for row in results]

        return list_results
    
    #find courses from category
    def search_course_category(self, search):
        #searches for any course category containing the keyword
        query = '''
            SELECT CourseID
            FROM Course
            WHERE Category LIKE CONCAT('%', %s, '%');
            '''
        
        self.cursor.execute(query, (search,))
        
        results = self.cursor.fetchall()

        #turn results from a list of tuples into just a list
        list_results = [row[0] for row in results]

        return list_results
    
    #find course from topic
    def search_course_topic(self, search):
        
        #Selects courses that have a topic that includes part of the keyword
        query = '''
            SELECT DISTINCT CourseID
            FROM Course
            JOIN CourseTopic USING (CourseID)
            JOIN Topic USING (TopicID)
            WHERE TopicName LIKE CONCAT('%', %s, '%');
            '''
        
        self.cursor.execute(query, (search,))
        
        results = self.cursor.fetchall()

        #turn results from a list of tuples into just a list
        list_results = [row[0] for row in results]

        return list_results
    
    #get course name given courseID
    def get_course_name(self, courseID):

        query = '''
            SELECT CourseName
            FROM Course
            WHERE CourseID = %s;
            '''
        
        self.cursor.execute(query, (courseID,))

        results = self.cursor.fetchone()

        #returns a course name
        return results


    #sort courses by rating
    def sort_courses_rating(self):

        query = '''
            SELECT CourseName
            FROM Course
            ORDER BY AverageRating DESC;
            '''
        
        self.cursor.execute(query)
        
        results = self.cursor.fetchall()

        #turn results from a list of tuples into just a list
        list_results = [row[0] for row in results]

        #returns a list of courses in descending rating order
        return list_results
    

    #view course info given course ID
    def retrieve_course_info(self, courseID):
        '''
        Must input courseID to retrieve course info

        Returns a tuple containing course name, description, category, instructor, and average rating in that order
        '''

        query = '''
            SELECT CourseName, Description, Category, Instructor, AverageRating
            FROM Course
            WHERE CourseID = %s;
            '''
        
        self.cursor.execute(query, (courseID,))

        results = self.cursor.fetchone()

        #returns a list containing CourseName, Description, Category, Instructor, AverageRating
        return results



#test
# 1. User Profile and Preferences Management
# Register/Login: Create an account(DONE) or log in with existing credentials.
# Edit Profile: Update personal details (e.g., name, email).(DONE)
# Set Interests: Select topics of interest to enhance recommendations.(DONE)
# View Learning History: Access a history of viewed, enrolled, or completed courses.(DONE)
# 2. Course Exploration and Search
# Search Courses: Find courses by keywords, topics, or categories.(DONE)
# Filter and Sort Courses: Filter courses by topic, rating (DONE), difficulty level, popularity, or duration.
# View Course Details: Access course information, including description, topics covered, rating, and reviews.(DONE except returns CourseName, Description, Category, Instructor, AverageRating)
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

