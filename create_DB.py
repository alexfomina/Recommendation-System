import mysql.connector

conn = mysql.connector.connect(host = 'localhost',
                               user = 'root',
                               password = 'CPSC408!',
                               auth_plugin = 'mysql_native_password')
                               #database = "RecommendationApp")

cur_obj = conn.cursor()

cur_obj.execute("CREATE SCHEMA RecommendationApp;")

cur_obj.execute("SHOW DATABASES;")

for row in cur_obj:
    print(row)


print(cur_obj)
conn.close()
