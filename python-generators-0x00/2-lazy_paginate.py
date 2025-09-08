import seed

def paginate_users(page_size: int, offset: int) -> list:

    connection = None
    try:
        connection = seed.connect_to_prodev()
        if connection:
            cursor = connection.cursor()
            query = f"SELECT * FROM user_data LIMIT %s OFFSET %s"
            cursor.execute(query, (page_size, offset))
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            dict_rows = [dict(zip(col_names, row)) for row in rows]
            cursor.close()
            return dict_rows
        return []
    except Exception as e:
        print(f"Error in paginate_users: {e}")
        return []
    finally:
        if connection:
            connection.close()


def lazy_pagination(page_size: int = 100):
  
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
