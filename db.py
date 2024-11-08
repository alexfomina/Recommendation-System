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
