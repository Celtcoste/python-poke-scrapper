import mysql.connector
import re
from ..utils.logger import debug, error, info

class Element:
    def __init__(self, name, image_uuid):
        self.name = name
        self.image_uuid = image_uuid

def create_element_slug(element_name: str) -> str:
    """Generate a slug from element name"""
    # Remove "Énergie" prefix if present
    slug = element_name.replace('Énergie ', '').replace('Energy ', '')

    # Convert to lowercase and normalize accents
    slug = slug.lower()
    slug = re.sub(r'[àâä]', 'a', slug)
    slug = re.sub(r'[éèêë]', 'e', slug)
    slug = re.sub(r'[îï]', 'i', slug)
    slug = re.sub(r'[ôö]', 'o', slug)
    slug = re.sub(r'[ùûü]', 'u', slug)
    slug = re.sub(r'[ç]', 'c', slug)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug

def insert_element_if_not_exists(conn, element_name: str, lang_id: int):
    """Insert element and its translation if they don't exist"""
    cursor = conn.cursor()
    try:
        # Generate slug from name
        slug = create_element_slug(element_name)

        # Check if element exists
        cursor.execute("SELECT id FROM element WHERE slug = %s LIMIT 1", (slug,))
        res = cursor.fetchone()

        if res is None:
            # Create new element
            cursor.execute("INSERT INTO element (slug) VALUES (%s)", (slug,))
            element_id = cursor.lastrowid
            info("Created new element: '%s' with slug '%s' and id %s", element_name, slug, element_id)
        else:
            element_id = res[0]
            debug("Element '%s' already exists with id %s", slug, element_id)

        # Check if translation exists
        translation_slug = f"{lang_id}/{slug}"
        cursor.execute(
            "SELECT id FROM element_translation WHERE element_id = %s AND translation_language_id = %s LIMIT 1",
            (element_id, lang_id)
        )
        trans_res = cursor.fetchone()

        if trans_res is None:
            # Create translation
            cursor.execute(
                "INSERT INTO element_translation (slug, element_id, name, translation_language_id) VALUES (%s, %s, %s, %s)",
                (translation_slug, element_id, element_name, lang_id)
            )
            info("Created new element translation: '%s' for language %s", element_name, lang_id)

        conn.commit()
        return element_id

    except mysql.connector.Error as err:
        error("Error creating element: %s", err)
        conn.rollback()
        return 0
    finally:
        cursor.close()

def get_element_id_by_name(conn, element_name: str, langId: int, auto_create: bool = True):
    """Get element ID by name, optionally creating it if it doesn't exist"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT element_id FROM element_translation WHERE name = %s AND translation_language_id = %s LIMIT 1",
            (element_name, langId,)
        )

        res = cursor.fetchone()

        if res is None:
            if auto_create:
                error("Element '%s' not found in database. Auto-creating...", element_name)
                return insert_element_if_not_exists(conn, element_name, langId)
            else:
                error("Element '%s' not found in database for language %s", element_name, langId)
                return 0

        element_id = res[0]
        return element_id

    except mysql.connector.Error as err:
        error("Error getting element_id: %s", err)
        conn.rollback()
        return 0

    finally:
        cursor.close()
