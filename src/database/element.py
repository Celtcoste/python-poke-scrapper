import mysql.connector

class Element:
    def __init__(self, name, image_uuid):
        self.name = name
        self.image_uuid = image_uuid

def get_element_id_by_name(conn, element_name: str, langId: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT element_id FROM element_translation WHERE name = %s AND language_id = %s LIMIT 1",
            (element_name, langId,)
        )   
        
        res = cursor.fetchone()
        if cursor.rowcount == -1:
            return 0
        id = res[0]
        return id

    except mysql.connector.Error as err:
        print(f"Error getting category_id: {err}")
        conn.rollback()

    finally:
        cursor.close()
        