import mysql.connector

def get_category_id_by_name(conn, category_name: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT category_id FROM category_translation WHERE name = %s LIMIT 1",
            (category_name,)
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