import uuid
import mysql.connector
from ..utils.logger import debug, error

def get_tcg_language_id_by_slug(conn, slug: str):
    """Get the tcg_language ID (integer) by slug"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM tcg_language WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting tcg_language id: %s", err)
        return None

    finally:
        cursor.close()

def get_bloc_id_by_slug(conn, slug: str):
    """Get existing bloc ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM bloc WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting bloc id: %s", err)
        return None

    finally:
        cursor.close()


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

def get_bloc_translation_id_by_slug(conn, slug: str):
    """Get existing bloc translation ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM bloc_translation WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting bloc translation id: %s", err)
        return None

    finally:
        cursor.close()

def insert_bloc_translation(conn, data: BlocTranslation):
    # Check if bloc translation already exists
    existing_id = get_bloc_translation_id_by_slug(conn, data.id)
    if existing_id is not None:
        debug("Bloc translation '%s' already exists with id: %s", data.id, existing_id)
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bloc_translation (slug, bloc_id, name, description, translation_language_id) VALUES (%s, %s, %s, %s, %s)",
            (data.id, data.bloc_id, data.name, data.description, data.language_id)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        error("Error creating bloc translation: %s", err)
        conn.rollback()
        return None

    finally:
        cursor.close()

def insert_bloc(conn, data: Bloc):
    # Check if bloc already exists
    existing_id = get_bloc_id_by_slug(conn, data.id)
    if existing_id is not None:
        debug("Bloc '%s' already exists with id: %s", data.id, existing_id)
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bloc (slug, tcg_language_id, serie_number, position) VALUES (%s, %s, %s, %s)",
            (data.id, data.tcg_id, data.set_number, data.position)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        error("Error creating bloc: %s", err)
        conn.rollback()
        return None

    finally:
        cursor.close()