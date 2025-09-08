import csv
import uuid
import MySQLdb





def connect_db():

    try: 
        con = MySQLdb.connect(
            host="localhost",
            user="root",
            passwd="Anas@063199",
            port=3306,
        ) 
        return con
    except MySQLdb.Error as e:
        print(f"Error connecting to MySQL Platform: {e}")
        return None
    

def create_database(con):
    try:
        cursor = con.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        cursor.close()
    except MySQLdb.Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """
    Connects directly to the ALX_prodev database.
    """
    try:
        connection = MySQLdb.connect(
            host="localhost",
            user="root",
            passwd="Anas@063199",
            db="ALX_prodev",
            port=3306
        )
        return connection
    except Exception as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None


def create_table(connection):
  

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL,
                INDEX (user_id)
            );
            """
        )
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except Exception as e:
        print(f"Error creating table: {e}")


def insert_data(connection, csv_file):

    try:
        cursor = connection.cursor()
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row["name"]
                email = row["email"]
                age = row["age"]

                # Check if email already exists
                cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
                if cursor.fetchone():
                    continue  # skip duplicates

                cursor.execute(
                    "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                    (user_id, name, email, age),
                )
        connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error inserting data: {e}")