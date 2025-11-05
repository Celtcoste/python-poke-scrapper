import mysql.connector
from ..utils.logger import debug, error

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
        error("Error getting rarity_id: %s", err)
        conn.rollback()


    finally:
        cursor.close()

# insert_card_rarity function removed - card_rarity table is redundant
# Cards have a single rarity stored in card.rarity_id