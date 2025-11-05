import mysql.connector
import re
from ..utils.logger import debug, error, info

class Rarity:
    def __init__(self, name, image_uuid):
        self.name = name
        self.image_uuid = image_uuid

def create_rarity_slug(rarity_name: str) -> str:
    """Generate a slug from rarity name"""
    # Convert to lowercase and replace spaces with hyphens
    slug = rarity_name.lower()
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

def insert_rarity_if_not_exists(conn, rarity_name: str, lang_id: int):
    """Insert rarity and its translation if they don't exist"""
    cursor = conn.cursor()
    try:
        # Generate slug from name
        slug = create_rarity_slug(rarity_name)

        # Check if rarity exists
        cursor.execute("SELECT id FROM rarity WHERE slug = %s LIMIT 1", (slug,))
        res = cursor.fetchone()

        if res is None:
            # Create new rarity
            cursor.execute("INSERT INTO rarity (slug) VALUES (%s)", (slug,))
            rarity_id = cursor.lastrowid
            info("Created new rarity: '%s' with slug '%s' and id %s", rarity_name, slug, rarity_id)
        else:
            rarity_id = res[0]
            debug("Rarity '%s' already exists with id %s", slug, rarity_id)

        # Check if translation exists
        translation_slug = f"{lang_id}/{slug}"
        cursor.execute(
            "SELECT id FROM rarity_translation WHERE rarity_id = %s AND translation_language_id = %s LIMIT 1",
            (rarity_id, lang_id)
        )
        trans_res = cursor.fetchone()

        if trans_res is None:
            # Create translation
            cursor.execute(
                "INSERT INTO rarity_translation (slug, rarity_id, name, translation_language_id) VALUES (%s, %s, %s, %s)",
                (translation_slug, rarity_id, rarity_name, lang_id)
            )
            info("Created new rarity translation: '%s' for language %s", rarity_name, lang_id)

        conn.commit()
        return rarity_id

    except mysql.connector.Error as err:
        error("Error creating rarity: %s", err)
        conn.rollback()
        return 0
    finally:
        cursor.close()

def get_rarity_id_by_name(conn, rarity_name: str, lang_id: int = 1, auto_create: bool = True):
    """Get rarity ID by name, optionally creating it if it doesn't exist"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT rarity_id FROM rarity_translation WHERE name = %s AND translation_language_id = %s LIMIT 1",
            (rarity_name, lang_id)
        )
        res = cursor.fetchone()

        if res is None:
            if auto_create:
                error("Rarity '%s' not found in database. Auto-creating...", rarity_name)
                return insert_rarity_if_not_exists(conn, rarity_name, lang_id)
            else:
                error("Rarity '%s' not found in database for language %s", rarity_name, lang_id)
                return 0

        rarity_id = res[0]
        return rarity_id

    except mysql.connector.Error as err:
        error("Error getting rarity_id: %s", err)
        conn.rollback()
        return 0

    finally:
        cursor.close()

# insert_card_rarity function removed - card_rarity table is redundant
# Cards have a single rarity stored in card.rarity_id