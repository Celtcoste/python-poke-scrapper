import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error
        
def create_connection():
    load_dotenv()
    connection = None
    try:
        connection = mysql.connector.connect(
        host=os.environ['DATABASE_ADDRESS'],
        port= os.environ['DATABASE_PORT'],
        user=os.environ['DATABASE_USERNAME'],
        password=os.environ['DATABASE_PASSWORD'],
        database=os.environ['DATABASE_NAME']
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection
    