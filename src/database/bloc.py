import uuid
import mysql.connector


class Bloc:
    def __init__(
        self, id, set_number, 
        position, tcg_id,
    ):
        self.id = id
        self.set_number = set_number
        self.position = position
        self.tcg_id = tcg_id

class BlocTranslation:
    def __init__(
        self, id, bloc_id, name, description, language_id
    ):
        self.id = id
        self.bloc_id = bloc_id
        self.name = name
        self.description = description
        self.language_id = language_id

def insert_bloc_translation(conn, data: BlocTranslation):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bloc_translation (id, bloc_id, name, description, language_id) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (data.id, data.bloc_id, data.name, data.description, data.language_id)
        )
        # Valider les changements
        conn.commit()
        return data.id
    
    except mysql.connector.Error as err:
        print(f"Error creating bloc translation: {err}")
        conn.rollback()
        

    finally:
        cursor.close()

def insert_bloc(conn, data: Bloc):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bloc (id, tcg_id, serie_number, position) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (data.id, data.tcg_id, data.set_number, data.position)
        )
        # Valider les changements
        conn.commit()
        return data.id
    
    except mysql.connector.Error as err:
        print(f"Error creating bloc: {err}")
        conn.rollback()

    finally:
        cursor.close()