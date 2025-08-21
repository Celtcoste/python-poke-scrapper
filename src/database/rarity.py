import mysql.connector

class Rarity:
    def __init__(self, name, image_uuid):
        self.name = name
        self.image_uuid = image_uuid
        
def get_rarity_id_by_name(conn, rarity_name: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT rarity_id FROM rarity_translation WHERE name = %s LIMIT 1",
            (rarity_name,)
        ) 
        res = cursor.fetchone()
        if cursor.rowcount == -1:
            return 0
        id = res[0]
        return id


    except mysql.connector.Error as err:
        print(f"Error getting rarity_id: {err}")
        conn.rollback()


    finally:
        cursor.close()

def insert_card_rarity(conn, card_id: str, rarity_name: str):
    """Insert card rarity relationship, matching rarity_name with rarity_translation.name"""
    cursor = conn.cursor()
    try:
        # First get the rarity_id from rarity_translation by matching the name
        cursor.execute(
            "SELECT rarity_id FROM rarity_translation WHERE name = %s LIMIT 1",
            (rarity_name,)
        )
        res = cursor.fetchone()
        if res is None:
            print(f"Warning: Rarity '{rarity_name}' not found in rarity_translation table")
            return None
        
        rarity_id = res[0]
        
        # Insert into card_rarity table with duplicate handling
        cursor.execute(
            "INSERT INTO card_rarity (card_id, rarity_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE card_id=card_id",
            (card_id, rarity_id)
        )
        conn.commit()
        return rarity_id
        
    except mysql.connector.Error as err:
        print(f"Error creating card rarity relationship: {err}")
        conn.rollback()
        return None
    
    finally:
        cursor.close()