import mysql.connector
import uuid
from ..utils.logger import debug, error

class Illustrator:
    def __init__(self, name):
        self.name = name
        
def get_illustrator_id(conn, data: Illustrator):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM illustrator WHERE name = %s",
            (data.name,)
        )   
        res = cursor.fetchone()
        if cursor.rowcount == -1:
            return 0
            
        id = res[0]
        return id


    except mysql.connector.Error as err:
        error("Error getting illustrator: %s", err)
        conn.rollback()

    finally:
        cursor.close()

def insert_illustrator(conn, data: Illustrator):
    cursor = conn.cursor()
    try:
        id = get_illustrator_id(conn, data)
        if id == 0:
            cursor.execute(
                "INSERT INTO illustrator (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=id",
                (data.name,)
            )
            conn.commit()
            id = get_illustrator_id(conn, data)
        return id

    except mysql.connector.Error as err:
        error("Error creating illustrator: %s", err)
        conn.rollback()

    finally:
        cursor.close()