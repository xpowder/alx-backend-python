import seed  

def stream_users_in_batches(batch_size):
  
    connection = seed.connect_to_prodev()
    if not connection:
        return

    cursor = connection.cursor()  
    offset = 0

    while True:
        cursor.execute(
            "SELECT user_id, name, email, age FROM user_data ORDER BY name LIMIT %s OFFSET %s",
            (batch_size, offset)
        )
        rows = cursor.fetchall()
        if not rows:
            break

       
        col_names = [desc[0] for desc in cursor.description]
        for row in rows:
            yield dict(zip(col_names, row))  
        offset += batch_size

    cursor.close()
    connection.close()


def batch_processing(batch_size):
  
    for user in stream_users_in_batches(batch_size):  
        if user['age'] > 25:
            print(user)  
