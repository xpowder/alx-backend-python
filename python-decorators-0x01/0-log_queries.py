#!/usr/bin/python3
import sqlite3
import functools



def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'query' in kwargs:
            query = kwargs['query']
        
        elif len(args) > 0:
            query = args[0]
        
        else:
            query = 'No query provided'

        
        print(f"Executing query: {query}")
        return func(*args, **kwargs)
    
    return wrapper



@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results



if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)