#!/usr/bin/python3
import sqlite3
import functools




def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        con = sqlite3.connect('users.db')
        try:
            result = func(con, *args, **kwargs)
        finally:
            con.close()
        return result
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)