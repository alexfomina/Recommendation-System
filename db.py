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

