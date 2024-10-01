import mysql.connector

class Game:
    def __init__(self, name, bloc_number, image_uuid):
        self.name = name
        self.bloc_number = bloc_number
        self.image_uuid = image_uuid
        
def insert_game(conn, data: Game):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO game (name, bloc_number, image_uuid) VALUES (%s, %s, %s)",
            (data.name, data.bloc_number, data.image_uuid)
        )
        id = cursor.lastrowid
        # Valider les changements
        conn.commit()
        return id
    
    
    except mysql.connector.Error as err:
        print(f"Error creating game: {err}")
        conn.rollback()


    finally:
        cursor.close()