import MySQLdb
from MySQLdb.cursors import DictCursor
import seed  

def stream_users():
 
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        if not connection:
            return

        cursor = connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM user_data ORDER BY name;")

        for row in cursor:
            yield row

    except Exception as e:
        print(f"An error occurred while streaming users: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
