import os
import mysql.connector as database

username = os.environ.get("username")
password = os.environ.get("password")

connection = database.connect(
    user=username,
    password=password,
    host=localhost,
    database="testdb")

cursor = connection.cursor()


def add_data(statement):
    try:
        cursor.execute(statement)
        connection.commit()
    except database.Error as e:
        print(f"Error adding entry to database: {e}")


connection.close()