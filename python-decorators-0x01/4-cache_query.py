#!/usr/bin/python3
import time
import sqlite3
import functools

query_cache = {}


def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper


def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get("query")
        if query is None and len(args) > 1:
            query = args[1]
        if query in query_cache:
            print(f"Using cached result for query: {query}")
            return query_cache[query]

        result = func(*args, **kwargs)
        query_cache[query] = result
        print(f"Caching result for query: {query}")
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(users)

    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(users_again)
