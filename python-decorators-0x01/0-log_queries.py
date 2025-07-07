#!/usr/bin/env python3
"""
Task 0: Logging Database Queries
Create a decorator that logs database queries executed by any function.
"""

import sqlite3
import functools

def log_queries(func):
    """
    Decorator to log SQL queries before executing them.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function that logs queries
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from the function arguments
        # Assume the query is passed as a keyword argument or the first positional argument
        query = None
        if 'query' in kwargs:
            query = kwargs['query']
        elif args and isinstance(args[0], str):
            query = args[0]
        elif len(args) > 1 and isinstance(args[1], str):
            query = args[1]
        
        if query:
            print(f"Executing SQL Query: {query}")
        
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    """Fetch all users from the database with the given query."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Found {len(users)} users")
    for user in users[:3]:  # Show first 3 users
        print(user)
