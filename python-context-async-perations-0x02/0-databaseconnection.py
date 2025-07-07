#!/usr/bin/env python3
"""
Task 0: Custom Class-Based Context Manager for Database Connection
Objective: Create a class-based context manager to handle opening and closing 
database connections automatically.
"""

import sqlite3

class DatabaseConnection:
    """
    A custom context manager for handling database connections.
    
    This class implements the context manager protocol using __enter__ and __exit__
    methods to automatically handle opening and closing database connections.
    """
    
    def __init__(self, database_name):
        """
        Initialize the DatabaseConnection context manager.
        
        Args:
            database_name (str): The name of the database file to connect to
        """
        self.database_name = database_name
        self.connection = None
    
    def __enter__(self):
        """
        Enter the context manager - open the database connection.
        
        Returns:
            sqlite3.Connection: The database connection object
        """
        print(f"Opening database connection to {self.database_name}")
        self.connection = sqlite3.connect(self.database_name)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - close the database connection.
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        
        Returns:
            None
        """
        if self.connection:
            if exc_type is not None:
                print(f"An error occurred: {exc_val}")
                self.connection.rollback()
            else:
                self.connection.commit()
            
            print(f"Closing database connection to {self.database_name}")
            self.connection.close()
        
        # Return False to propagate any exceptions
        return False

def main():
    """
    Demonstrate the DatabaseConnection context manager by executing a query.
    """
    print("=== Database Connection Context Manager Demo ===\n")
    
    # Use the context manager with the 'with' statement
    with DatabaseConnection('users.db') as conn:
        print("Inside the context manager - connection is active")
        
        # Create a cursor and execute the query
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        
        # Fetch and print all results
        results = cursor.fetchall()
        print(f"\nQuery Results - Found {len(results)} users:")
        print("-" * 50)
        
        for user in results:
            print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Age: {user[3]}")
    
    print("\nContext manager has automatically closed the connection")

if __name__ == "__main__":
    main()
