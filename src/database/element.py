import mysql.connector
from ..utils.logger import debug, error

class Element:
    def __init__(self, name, image_uuid):
        self.name = name
        self.image_uuid = image_uuid

def get_element_id_by_name(conn, element_name: str, langId: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT element_id FROM element_translation WHERE name = %s AND translation_language_id = %s LIMIT 1",
            (element_name, langId,)
        )   
        
        res = cursor.fetchone()
        if cursor.rowcount == -1:
            return 0
        id = res[0]
        return id

    except mysql.connector.Error as err:
        error("Error getting element_id: %s", err)
        conn.rollback()

    finally:
        cursor.close()
        