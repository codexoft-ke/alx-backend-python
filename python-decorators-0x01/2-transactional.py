#!/usr/bin/env python3
"""
Task 2: Transaction Management Decorator
Create a decorator that manages database transactions by automatically 
committing or rolling back changes.
"""

import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles database connection management.
    Opens a connection, passes it to the function, and closes it afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    
    return wrapper

def transactional(func):
    """
    Decorator that manages database transactions.
    Automatically commits on success or rolls back on error.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with transaction management
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Begin transaction (SQLite uses autocommit=False by default)
            result = func(conn, *args, **kwargs)
            # Commit the transaction if successful
            conn.commit()
            print("Transaction committed successfully")
            return result
        except Exception as e:
            # Rollback the transaction on error
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")
            raise  # Re-raise the exception
    
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Update a user's email address."""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    # Check if any rows were affected
    if cursor.rowcount == 0:
        raise ValueError(f"No user found with ID {user_id}")

if __name__ == "__main__":
    # Update user's email with automatic transaction handling
    try:
        update_user_email(user_id=1, new_email='crawford_cartwright@hotmail.com')
        print("Email updated successfully")
    except Exception as e:
        print(f"Failed to update email: {e}")
