#!/usr/bin/env python3
"""
Task 4: Using Decorators to Cache Database Queries
Create a decorator that caches the results of database queries to avoid redundant calls.
"""

import time
import sqlite3
import functools

# Global cache dictionary
query_cache = {}

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

def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with caching capability
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key based on function name and arguments
        # Extract the query from kwargs or args
        query = None
        if 'query' in kwargs:
            query = kwargs['query']
        else:
            # Look for query in positional arguments (usually the last argument)
            for arg in args:
                if isinstance(arg, str) and ('SELECT' in arg.upper() or 'INSERT' in arg.upper() or 'UPDATE' in arg.upper()):
                    query = arg
                    break
        
        if query:
            # Create cache key using function name and query
            cache_key = f"{func.__name__}:{query}"
            
            # Check if result is already cached
            if cache_key in query_cache:
                print(f"Cache hit! Returning cached result for query: {query}")
                return query_cache[cache_key]
            
            # Execute function and cache result
            print(f"Cache miss! Executing query: {query}")
            result = func(*args, **kwargs)
            query_cache[cache_key] = result
            print(f"Result cached for future use")
            return result
        else:
            # If no query found, just execute without caching
            return func(*args, **kwargs)
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Fetch users from the database with caching."""
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Additional cached function for demonstration
@with_db_connection
@cache_query
def get_user_by_id_cached(conn, user_id):
    """Get a user by ID with caching."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

def clear_cache():
    """Utility function to clear the query cache."""
    global query_cache
    query_cache.clear()
    print("Query cache cleared")

def show_cache_stats():
    """Show current cache statistics."""
    print(f"Cache contains {len(query_cache)} entries:")
    for key in query_cache.keys():
        print(f"  - {key}")

if __name__ == "__main__":
    print("=== Cache Query Decorator Demo ===\n")
    
    # First call will cache the result
    print("1. First call - will be cached:")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Found {len(users)} users\n")
    
    # Second call will use the cached result
    print("2. Second call - will use cache:")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Found {len(users_again)} users\n")
    
    # Different query will not use cache
    print("3. Different query - will not use cache:")
    limited_users = fetch_users_with_cache(query="SELECT * FROM users LIMIT 3")
    print(f"Found {len(limited_users)} users\n")
    
    # Same limited query will use cache
    print("4. Same limited query - will use cache:")
    limited_users_again = fetch_users_with_cache(query="SELECT * FROM users LIMIT 3")
    print(f"Found {len(limited_users_again)} users\n")
    
    # Show cache statistics
    show_cache_stats()
    
    # Demonstrate cache clearing
    print("\n5. Clearing cache...")
    clear_cache()
    
    # After clearing, same query will execute again
    print("\n6. After cache clear - will execute again:")
    users_after_clear = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Found {len(users_after_clear)} users")
