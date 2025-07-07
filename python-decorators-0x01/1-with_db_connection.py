#!/usr/bin/env python3
"""
Task 1: Handle Database Connections with a Decorator
Create a decorator that automatically handles opening and closing database connections.
"""

import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles database connection management.
    Opens a connection, passes it to the function, and closes it afterward.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with automatic connection handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass connection as the first argument to the decorated function
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection
            conn.close()
    
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    """Get a user by their ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

if __name__ == "__main__":
    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    print(f"User found: {user}")
