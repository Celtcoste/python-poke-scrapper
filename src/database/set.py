import uuid
import mysql.connector

class SetTranslation:
    def __init__(self, id, set_id, name, description, language_id):
        self.id = id
        self.set_id = set_id
        self.name = name
        self.description = description
        self.language_id = language_id

class Set:
    def __init__(self, id, card_number, position, bloc_id):
        self.id = id
        self.card_number = card_number
        self.position = position
        self.bloc_id = bloc_id
  
def insert_set_translation(conn, data: SetTranslation):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO `serie_translation` (id, serie_id, name, description, language_id) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (data.id, data.set_id, data.name, data.description, data.language_id)
        )
        # Valider les changements
        conn.commit()
        return data.id

    except mysql.connector.Error as err:
        print(f"Error creating set translation: {err}")
        conn.rollback()

    finally:
        cursor.close()
        
def insert_set(conn, data: Set):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO `serie` (id, card_number, position, bloc_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (data.id, data.card_number, data.position, data.bloc_id)
        )
        # Valider les changements
        conn.commit()
        return data.id


    except mysql.connector.Error as err:
        print(f"Error creating set: {err}")
        conn.rollback()


    finally:
        cursor.close()