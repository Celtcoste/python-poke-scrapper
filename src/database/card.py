import mysql.connector
import uuid
import re
from ..utils.logger import debug, error

from .element import get_element_id_by_name

def clean_slug_format(slug: str) -> str:
    """Clean slug format by removing leading zeros from numbers"""
    # Split the slug by '/' and process each part
    parts = slug.split('/')
    cleaned_parts = []
    
    for part in parts:
        # Remove leading zeros from numbers (001 -> 1, sv01 -> sv1)
        # This regex finds sequences of letters followed by numbers and removes leading zeros
        cleaned_part = re.sub(r'(\D*)0*(\d+)', r'\1\2', part)
        # Handle pure numbers (001 -> 1)
        if part.isdigit():
            cleaned_part = str(int(part))
        cleaned_parts.append(cleaned_part)
    
    return '/'.join(cleaned_parts)

def clean_seo_name(name: str) -> str:
    """Clean name for SEO path usage - matches SQL script logic"""
    import re
    
    if not name:
        return ''
    
    # Convert to lowercase and trim
    cleaned = name.lower().strip()
    
    # Character replacements (matching SQL script)
    replacements = {
        'à': 'a', 'â': 'a', 
        'é': 'e', 'è': 'e', 'ê': 'e',
        'ï': 'i', 'î': 'i',
        'ô': 'o',
        'ù': 'u',
        'ç': 'c',
        'æ': 'ae',
        'œ': 'oe',
        '☆': 'star',
        '★': 'star', 
        'δ': 'delta',
        '◇': 'prism'
    }
    
    # Apply character replacements
    for old_char, new_char in replacements.items():
        cleaned = cleaned.replace(old_char, new_char)
    
    # Remove special characters: ()[]., +?!&♀♂#
    cleaned = re.sub(r'[()[\].+?!&♀♂#]', '', cleaned)
    
    # Replace any non-alphanumeric characters with hyphens
    cleaned = re.sub(r'[^a-zA-Z0-9]', '-', cleaned)
    
    # Replace multiple consecutive hyphens with single hyphen
    cleaned = re.sub(r'-{2,}', '-', cleaned)
    
    # Remove trailing hyphen
    cleaned = re.sub(r'-$', '', cleaned)
    
    # Remove leading hyphen
    cleaned = re.sub(r'^-', '', cleaned)
    
    return cleaned

def get_card_seo_data(conn, card_id: str, language_id: str):
    """Get all the data needed to build the SEO path for a card"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.position as card_position,
                s.card_number as serie_card_count,
                st.name as serie_name,
                bt.name as bloc_name,
                tl.slug as tcg_language_slug
            FROM card c
            JOIN serie s ON c.serie_id = s.id
            JOIN serie_translation st ON s.id = st.serie_id AND st.translation_language_id = %s
            JOIN bloc b ON s.bloc_id = b.id
            JOIN bloc_translation bt ON b.id = bt.bloc_id AND bt.translation_language_id = %s
            JOIN tcg_language tl ON b.tcg_language_id = tl.id
            WHERE c.id = %s
        """, (language_id, language_id, card_id))
        
        result = cursor.fetchone()
        if result:
            return {
                'card_position': result[0],
                'serie_card_count': result[1], 
                'serie_name': result[2],
                'bloc_name': result[3],
                'tcg_language_slug': result[4]
            }
        return None
        
    except mysql.connector.Error as err:
        error("Error getting card SEO data: %s", err)
        return None
    finally:
        cursor.close()

def build_seo_path(card_name: str, seo_data: dict) -> str:
    """Build SEO path from card data"""
    if not seo_data:
        # Fallback to simple name-based SEO path
        return clean_seo_name(card_name)
    
    # Clean all components
    clean_card_name = clean_seo_name(card_name)
    clean_serie_name = clean_seo_name(seo_data['serie_name'])
    clean_bloc_name = clean_seo_name(seo_data['bloc_name'])
    clean_tcg_slug = clean_seo_name(seo_data['tcg_language_slug'])
    
    # Format: {card_name}-{card_position}-{serie_card_count}-{serie_name}-{bloc_name}-{tcg_language_slug}
    seo_path = f"{clean_card_name}-{seo_data['card_position']}-{seo_data['serie_card_count']}-{clean_serie_name}-{clean_bloc_name}-{clean_tcg_slug}"
    
    # Replace only the last occurrence of "poke-{lang}" with "pokemon-{lang}" for better SEO
    # This targets the tcg_language_slug at the end, not card names like "poke-ball"
    import re
    seo_path = re.sub(r'-poke-(fr|en|jp)$', r'-pokemon-\1', seo_path)
    
    return seo_path

def get_card_id_by_slug(conn, slug: str):
    """Get existing card ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM card WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting card id: %s", err)
        return None

    finally:
        cursor.close()

def get_card_translation_id_by_slug(conn, slug: str):
    """Get existing card translation ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM card_translation WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        error("Error getting card translation id: %s", err)
        return None

    finally:
        cursor.close()


class PokemonCard:
    def __init__(self, id, card_id, pokemon_id, hp, level):
        self.id = id
        self.card_id = card_id
        self.pokemon_id = pokemon_id
        self.hp = hp
        self.level = level

class Card:
    def __init__(self, id, position, category_id, rarity_id, set_id, illustrator_id):
        self.id = id
        self.position = position
        self.category_id = category_id
        self.rarity_id = rarity_id
        self.set_id = set_id
        self.illustrator_id = illustrator_id
 
def check_energy_card(conn, id: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM energy_card WHERE card_id = %s LIMIT 1",
            (id,)
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
        
def check_trainer_card(conn, id: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM trainer_card WHERE card_id = %s LIMIT 1",
            (id,)
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
        
def check_pokemon_card(conn, id: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM pokemon_card WHERE card_id = %s LIMIT 1",
            (id,)
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
        
def get_card_id(conn, id: str):
    """Legacy function for backward compatibility - now uses slug-based lookup"""
    # Clean the slug format and use the new function
    cleaned_slug = clean_slug_format(id)
    result = get_card_id_by_slug(conn, cleaned_slug)
    # Return 0 for not found to maintain backward compatibility
    return result if result is not None else 0
        
def insert_card(conn, data: Card):
    # Clean the slug format
    cleaned_slug = clean_slug_format(data.id)
    
    # Check if card already exists
    existing_id = get_card_id_by_slug(conn, cleaned_slug)
    if existing_id is not None:
        debug("Card '%s' already exists with id: %s", cleaned_slug, existing_id)
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO card (slug, position, category_id, rarity_id, serie_id, illustrator_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (cleaned_slug, data.position, data.category_id, data.rarity_id, data.set_id, data.illustrator_id)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        print(f"Error creating card: {err}")
        conn.rollback()
        return None

    finally:
        cursor.close()
        
def insert_card_translation(conn, slug: str, card_id: str, language_id: str, name: str, description: str):
    # Clean the slug format
    cleaned_slug = clean_slug_format(slug)
    
    # Check if card translation already exists
    existing_id = get_card_translation_id_by_slug(conn, cleaned_slug)
    if existing_id is not None:
        debug("Card translation '%s' already exists with id: %s", cleaned_slug, existing_id)
        return existing_id
    
    cursor = conn.cursor()
    try:
        # Get card SEO data for building complex SEO path
        seo_data = get_card_seo_data(conn, card_id, language_id)
        seo_path = build_seo_path(name, seo_data)
        
        debug("Generated SEO path: %s for card: %s", seo_path, name)
        
        cursor.execute(
            "INSERT INTO card_translation (slug, seo_path, card_id, translation_language_id, name, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (cleaned_slug, seo_path, card_id, language_id, name, description)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        error("Error creating card translation: %s", err)
        conn.rollback()
        return None

    finally:
        cursor.close()
        
def get_energy_card_id_by_slug(conn, slug: str):
    """Get existing energy card ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM energy_card WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        print(f"Error getting energy card id: {err}")
        return None

    finally:
        cursor.close()

def insert_energy_card(conn, slug: str, card_id: str, energy_type: str, langId: str):
    # Clean the slug format
    cleaned_slug = clean_slug_format(slug)
    
    # Check if energy card already exists
    existing_id = get_energy_card_id_by_slug(conn, cleaned_slug)
    if existing_id is not None:
        print(f"Energy card '{cleaned_slug}' already exists with id: {existing_id}")
        return existing_id
    
    cursor = conn.cursor()
    try:
        element_id = get_element_id_by_name(conn, energy_type.split(' ')[0], langId)
        if element_id == 0 and len(energy_type.split(' ')) > 1:
            element_id = get_element_id_by_name(conn, energy_type.split(' ')[1], langId)
        if element_id == 0:
            element_id = get_element_id_by_name(conn, "Special", langId)
        cursor.execute(
            "INSERT INTO energy_card (slug, card_id, element_id) VALUES (%s, %s, %s)",
            (cleaned_slug, card_id, element_id)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        print(f"Error creating energy card: {err}")
        conn.rollback()
        return None

    finally:
        cursor.close()
                
def get_trainer_card_id_by_slug(conn, slug: str):
    """Get existing trainer card ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM trainer_card WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        print(f"Error getting trainer card id: {err}")
        return None

    finally:
        cursor.close()

def insert_trainer_card(conn, slug: str, card_id: str):
    # Clean the slug format
    cleaned_slug = clean_slug_format(slug)
    
    # Check if trainer card already exists
    existing_id = get_trainer_card_id_by_slug(conn, cleaned_slug)
    if existing_id is not None:
        print(f"Trainer card '{cleaned_slug}' already exists with id: {existing_id}")
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO trainer_card (slug, card_id) VALUES (%s, %s)",
            (cleaned_slug, card_id)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        print(f"Error creating trainer card: {err}")
        conn.rollback()
        return None

    finally:
        cursor.close()
        
def get_pokemon_card_id_by_slug(conn, slug: str):
    """Get existing pokemon card ID by slug to handle duplicates"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM pokemon_card WHERE slug = %s LIMIT 1",
            (slug,)
        )   
        res = cursor.fetchone()
        if res is None:
            return None
        return res[0]

    except mysql.connector.Error as err:
        print(f"Error getting pokemon card id: {err}")
        return None

    finally:
        cursor.close()

def insert_pokemon_card(conn, data: PokemonCard):
    # Clean the slug format
    cleaned_slug = clean_slug_format(data.id)
    
    # Check if pokemon card already exists
    existing_id = get_pokemon_card_id_by_slug(conn, cleaned_slug)
    if existing_id is not None:
        print(f"Pokemon card '{cleaned_slug}' already exists with id: {existing_id}")
        return existing_id
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pokemon_card (slug, card_id, pokemon_id, hp, level) VALUES (%s, %s, %s, %s, %s)",
            (cleaned_slug, data.card_id, data.pokemon_id, data.hp, data.level)
        )
        # Valider les changements
        conn.commit()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        print(f"Error creating pokemon card: {err}")
        conn.rollback()
        return None

    finally:
        cursor.close()
        

def insert_pokemon_card_element(conn, pokemon_card_id: str, element: str, langId: str):
    cursor = conn.cursor()
    try:
        element_id = get_element_id_by_name(conn, element, langId)
        if element_id == 0:
            element_id = get_element_id_by_name(conn, element, langId)
            
        cursor.execute(
            "INSERT INTO pokemon_card_elements (pokemon_card_id, element_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE pokemon_card_id=pokemon_card_id",
            (pokemon_card_id, element_id)
        )
        # Valider les changements
        conn.commit()
        return 


    except mysql.connector.Error as err:
        print(f"Error creating pokemon card element: {err}")
        conn.rollback()


    finally:
        cursor.close()

def insert_card_variant(conn, card_id: str, variant: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO card_variants (card_id, variant_id) VALUES (%s, (SELECT id FROM variant WHERE name = %s)) ON DUPLICATE KEY UPDATE card_id=card_id",
            (card_id, variant)
        )
        # Valider les changements
        conn.commit()
        return 


    except mysql.connector.Error as err:
        print(f"Error creating pokemon card element: {err}")
        conn.rollback()


    finally:
        cursor.close()