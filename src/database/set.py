import uuid
import mysql.connector
from ..utils.logger import debug, error

def get_set_id_by_slug(conn, slug: str):
    """Get existing set ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM `serie` WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting set id: %s", err)
        return None

    finally:
        cursor.close()

def get_set_translation_id_by_slug(conn, slug: str):
    """Get existing set translation ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM `serie_translation` WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting set translation id: %s", err)
        return None

    finally:
        cursor.close()

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
    # Check if set translation already exists
    existing_id = get_set_translation_id_by_slug(conn, data.id)
    if existing_id is not None:
        debug("Set translation '%s' already exists with id: %s", data.id, existing_id)
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO `serie_translation` (slug, serie_id, name, description, translation_language_id) VALUES (%s, %s, %s, %s, %s)",
            (data.id, data.set_id, data.name, data.description, data.language_id)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid

    except mysql.connector.Error as err:
        error("Error creating set translation: %s", err)
        conn.rollback()
        return None

    finally:
        cursor.close()
        
def insert_set(conn, data: Set):
    # Check if set already exists
    existing_id = get_set_id_by_slug(conn, data.id)
    if existing_id is not None:
        debug("Set '%s' already exists with id: %s", data.id, existing_id)
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO `serie` (slug, card_number, position, bloc_id) VALUES (%s, %s, %s, %s)",
            (data.id, data.card_number, data.position, data.bloc_id)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid

    except mysql.connector.Error as err:
        error("Error creating set: %s", err)
        conn.rollback()
        return None

    finally:
        cursor.close()