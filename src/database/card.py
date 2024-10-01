import mysql.connector
import uuid

from .element import get_element_id_by_name


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
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM card WHERE id = %s LIMIT 1",
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
        
def insert_card(conn, data: Card):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO card (id, position, category_id, rarity_id, set_id, illustrator_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (data.id, data.position, data.category_id, data.rarity_id, data.set_id, data.illustrator_id)
        )
        # Valider les changements
        conn.commit()
        return data.id
    
    except mysql.connector.Error as err:
        print(f"Error creating card: {err}")
        conn.rollback()

    finally:
        cursor.close()
        
def insert_card_translation(conn, id: str, card_id: str, language_id: str, name: str, description: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO card_translation (id, card_id, language_id, name, description) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (id, card_id, language_id, name, description)
        )
        # Valider les changements
        conn.commit()
        return id
    
    except mysql.connector.Error as err:
        print(f"Error creating card: {err}")
        conn.rollback()

    finally:
        cursor.close()
        
def insert_energy_card(conn, id: str, card_id: str, energy_type: str, langId: str):
    cursor = conn.cursor()
    try:
        element_id = get_element_id_by_name(conn, energy_type.split(' ')[0], langId)
        if element_id == 0 and len(energy_type.split(' ')) > 1:
            element_id = get_element_id_by_name(conn, energy_type.split(' ')[1], langId)
        if element_id == 0:
            element_id = get_element_id_by_name(conn, "Special", langId)
        cursor.execute(
            "INSERT INTO energy_card (id, card_id, element_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (id, card_id, element_id)
        )
        # Valider les changements
        conn.commit()
        return id
    
    except mysql.connector.Error as err:
        print(f"Error creating energy card: {err}")
        conn.rollback()

    finally:
        cursor.close()
                
def insert_trainer_card(conn, id: str, card_id: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO trainer_card (id, card_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id=id",
            (id, card_id)
        )
        # Valider les changements
        conn.commit()
        return id
    
    except mysql.connector.Error as err:
        print(f"Error creating trainer card: {err}")
        conn.rollback()

    finally:
        cursor.close()
        
def insert_pokemon_card(conn, data: PokemonCard):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pokemon_card (id, card_id, pokemon_id, hp, level) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (data.id, data.card_id, data.pokemon_id, data.hp, data.level)
        )
        # Valider les changements
        conn.commit()
        return data.id
    
    except mysql.connector.Error as err:
        print(f"Error creating pokemon card: {err}")
        conn.rollback()

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