import mysql.connector
import uuid
from ..utils.logger import debug, error

def get_pokemon_translation_id_by_slug(conn, slug: str):
    """Get existing pokemon translation ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM pokemon_translation WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting pokemon translation id: %s", err)
        return None

    finally:
        cursor.close()

def get_pokemon_id_by_dex_id(conn, dex_id: str):
    """Get existing pokemon ID by dex ID to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM pokemon WHERE id = %s LIMIT 1",
            (dex_id,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting pokemon id: %s", err)
        return None

    finally:
        cursor.close()

def get_pokemon_id_by_name(conn, pokemon_name: str, langId: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT pokemon_id FROM pokemon_translation WHERE name = %s AND translation_language_id = %s LIMIT 1",
            (pokemon_name, langId)
        )   
        res = cursor.fetchone()
        if cursor.rowcount == -1:
            return 0
        id = res[0]
        
        return id


    except mysql.connector.Error as err:
        error("Error getting pokemon by name: %s", err)
        conn.rollback()

    finally:
        cursor.close()
        
def insert_pokemon(conn, dexId: str):
    # Check if pokemon already exists by dex ID
    existing_id = get_pokemon_id_by_dex_id(conn, dexId)
    if existing_id is not None:
        debug("Pokemon with dex ID '%s' already exists with id: %s", dexId, existing_id)
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pokemon (id) VALUES (%s)",
            (dexId,)
        )
        # Valider les changements
        conn.commit()
        return int(dexId)
    
    except mysql.connector.Error as err:
        error("Error creating pokemon: %s", err)
        conn.rollback()
        return None

    finally:
        cursor.close()
        
def insert_pokemon_translation(conn, slug: str, pokemon_id: str, name: str, langId: str):
    # Check if pokemon translation already exists
    existing_id = get_pokemon_translation_id_by_slug(conn, slug)
    if existing_id is not None:
        debug("Pokemon translation '%s' already exists with id: %s", slug, existing_id)
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pokemon_translation (slug, pokemon_id, name, translation_language_id) VALUES (%s, %s, %s, %s)",
            (slug, pokemon_id, name, langId)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        error("Error creating pokemon translation: %s", err)
        conn.rollback()
        return None

    finally:
        cursor.close()

def insert_pokemon_if_not_exist(conn, dexId: str, transNewSlug: str, name: str, langId: str):
    """Insert pokemon and its translation if they don't exist"""
    try:
        # First check if pokemon translation already exists
        existing_translation_id = get_pokemon_translation_id_by_slug(conn, transNewSlug)
        if existing_translation_id is not None:
            debug("Pokemon translation '%s' already exists", transNewSlug)
            # Get the pokemon_id from existing translation
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT pokemon_id FROM pokemon_translation WHERE id = %s", (existing_translation_id,))
                result = cursor.fetchone()
                return result[0] if result else None
            finally:
                cursor.close()
        
        # Check if pokemon exists by name
        pokemon_id = get_pokemon_id_by_name(conn, name, langId)
        if pokemon_id == 0:
            # Create new pokemon
            pokemon_id = insert_pokemon(conn, dexId)
            if pokemon_id is None:
                error("Failed to create pokemon with dex ID: %s", dexId)
                return None
                
            # Create pokemon translation
            translation_id = insert_pokemon_translation(conn, transNewSlug, pokemon_id, name, langId)
            if translation_id is None:
                error("Failed to create pokemon translation: %s", transNewSlug)
                return None
        
        return pokemon_id
    
    except mysql.connector.Error as err:
        error("Error in insert_pokemon_if_not_exist: %s", err)
        return None