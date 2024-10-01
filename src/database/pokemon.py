import mysql.connector
import uuid

def get_pokemon_id_by_name(conn, pokemon_name: str, langId: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT pokemon_id FROM pokemon_translation WHERE name = %s AND language_id = %s LIMIT 1",
            (pokemon_name, langId)
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
        
def insert_pokemon(conn, dexId: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pokemon (id) VALUES (%s) ON DUPLICATE KEY UPDATE id=id",
            (dexId,)
        )
        # Valider les changements
        conn.commit()
        return dexId
    
    except mysql.connector.Error as err:
        print(f"Error creating card: {err}")
        conn.rollback()

    finally:
        cursor.close()
        
def insert_pokemon_translation(conn, id: str, pokemon_id: str, name: str, langId: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pokemon_translation (id, pokemon_id, name, language_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id",
            (id, pokemon_id, name, langId)
        )
        # Valider les changements
        conn.commit()
        return id
    
    except mysql.connector.Error as err:
        print(f"Error creating card: {err}")
        conn.rollback()

    finally:
        cursor.close()

def insert_pokemon_if_not_exist(conn, dexId: str, transNewId: str, name: str, langId: str):
    cursor = conn.cursor()
    try:
        id = get_pokemon_id_by_name(conn, name, langId)
        if id == 0:
            id = insert_pokemon(conn, dexId)
            insert_pokemon_translation(conn, transNewId, id, name, langId)
        return id
    
    except mysql.connector.Error as err:
        print(f"Error creating pokemon: {err}")
        conn.rollback()

    finally:
        cursor.close()