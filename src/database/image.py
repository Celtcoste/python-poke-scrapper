import mysql.connector
import uuid

class Image:
    def __init__(self, path, mime_type):
        self.path = path
        self.mime_type = mime_type
        
def insert_image(conn, data: Image):
    id = str(uuid.uuid4())
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO image (uuid, path, mime_type) VALUES (%s, %s, %s)",
            (id, data.path, data.mime_type)
        )

        # Valider les changements
        conn.commit()
        return id
    
    
    except mysql.connector.Error as err:
        print(f"Error creating image: {err}")
        conn.rollback()

    finally:
        cursor.close()