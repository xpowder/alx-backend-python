import seed  

def stream_user_ages():
  
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        if not connection:
            return

        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")

        for (age,) in cursor:
            yield age

    except Exception as e:
        print(f"An error occurred while streaming ages: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_average_age():
    total_age = 0
    user_count = 0


    for age in stream_user_ages():
        total_age += age
        user_count += 1

    average_age = total_age / user_count if user_count else 0
    print(f"Average age of users: {average_age:.2f}")


if __name__ == "__main__":
    calculate_average_age()
