#!/usr/bin/python3

import os
seed = __import__('seed')

connection = seed.connect_db()
if connection:
    seed.create_database(connection)
    connection.close()
    print("Connection to MySQL server successful")


connection = seed.connect_to_prodev()
if connection:
    seed.create_table(connection)

    csv_path = os.path.join(os.getcwd(), 'user_data.csv')  
    if not os.path.exists(csv_path):
        print(f"CSV file not found at {csv_path}")
    else:
        seed.insert_data(connection, csv_path)

    cursor = connection.cursor()
    cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'ALX_prodev';")
    if cursor.fetchone():
        print("Database ALX_prodev is present")

    cursor.execute("SELECT * FROM user_data LIMIT 5;")
    rows = cursor.fetchall()
    print(rows)

    cursor.close()
    connection.close()
