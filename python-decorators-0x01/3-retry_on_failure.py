#!/usr/bin/env python3
"""
Task 3: Using Decorators to Retry Database Queries
Create a decorator that retries database operations if they fail due to transient errors.
"""

import time
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

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function a certain number of times if it raises an exception.
    
    Args:
        retries (int): Number of retry attempts (default: 3)
        delay (int): Delay in seconds between retries (default: 2)
        
    Returns:
        The decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):  # +1 because we include the initial attempt
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        print(f"Operation succeeded on attempt {attempt + 1}")
                    return result
                except Exception as e:
                    last_exception = e
                    if attempt < retries:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print(f"All {retries + 1} attempts failed. Last error: {e}")
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """Fetch all users from the database with retry mechanism."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Function to simulate database failure for testing
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_simulated_failure(conn):
    """Fetch users but simulate intermittent failures."""
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise sqlite3.OperationalError("Simulated database connection error")
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

if __name__ == "__main__":
    # Attempt to fetch users with automatic retry on failure
    try:
        print("Fetching users with retry mechanism...")
        users = fetch_users_with_retry()
        print(f"Successfully fetched {len(users)} users")
        
        # Uncomment the line below to test with simulated failures
        # users = fetch_users_with_simulated_failure()
        
    except Exception as e:
        print(f"Failed to fetch users after all retries: {e}")
