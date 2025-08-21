import mysql.connector
from ..utils.logger import debug, error

# Mapping from API category names to database category names (French)
CATEGORY_NAME_MAPPING = {
    "Pokémon": "Pokémon",  # Assuming this exists in French
    "Energy": "Energie", 
    "Trainer": "Dresseur",  # Assuming this exists in French
    # Add more mappings as needed
}

def get_category_id_by_name(conn, category_name: str):
    """Get category ID by API category name, with proper name mapping"""
    cursor = conn.cursor()
    try:
        # Map API category name to database category name
        db_category_name = CATEGORY_NAME_MAPPING.get(category_name, category_name)
        
        debug("Looking for category: API='%s' -> DB='%s'", category_name, db_category_name)
        
        cursor.execute(
            "SELECT category_id FROM category_translation WHERE name = %s LIMIT 1",
            (db_category_name,)
        )   
        res = cursor.fetchone()
        
        if res is None:
            debug("Category not found. Let's see what categories exist:")
            cursor.execute("SELECT name, category_id FROM category_translation LIMIT 10")
            existing_categories = cursor.fetchall()
            debug("Existing categories: %s", existing_categories)
            return 0
            
        category_id = res[0]
        debug("Found category '%s' with ID: %s", db_category_name, category_id)
        return category_id

    except mysql.connector.Error as err:
        error("Error getting category_id: %s", err)
        conn.rollback()
        return 0

    finally:
        cursor.close()