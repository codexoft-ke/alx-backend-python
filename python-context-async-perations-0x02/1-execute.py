#!/usr/bin/env python3
"""
Task 1: Reusable Query Context Manager
Objective: Create a reusable context manager that takes a query as input and executes it,
managing both connection and the query execution.
"""

import sqlite3

class ExecuteQuery:
    """
    A reusable context manager for executing database queries.
    
    This class handles both database connection management and query execution,
    automatically managing resources using the context manager protocol.
    """
    
    def __init__(self, database_name, query, parameters=None):
        """
        Initialize the ExecuteQuery context manager.
        
        Args:
            database_name (str): The name of the database file to connect to
            query (str): The SQL query to execute
            parameters (tuple, optional): Parameters for the SQL query
        """
        self.database_name = database_name
        self.query = query
        self.parameters = parameters or ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - open connection and execute query.
        
        Returns:
            list: The results of the executed query
        """
        print(f"Opening connection to {self.database_name}")
        
        # Open database connection
        self.connection = sqlite3.connect(self.database_name)
        self.cursor = self.connection.cursor()
        
        # Execute the query
        print(f"Executing query: {self.query}")
        if self.parameters:
            print(f"With parameters: {self.parameters}")
            self.cursor.execute(self.query, self.parameters)
        else:
            self.cursor.execute(self.query)
        
        # Fetch all results
        self.results = self.cursor.fetchall()
        print(f"Query executed successfully, found {len(self.results)} results")
        
        return self.results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - close cursor and connection.
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        
        Returns:
            None
        """
        if self.cursor:
            self.cursor.close()
        
        if self.connection:
            if exc_type is not None:
                print(f"An error occurred: {exc_val}")
                self.connection.rollback()
            else:
                self.connection.commit()
            
            print(f"Closing connection to {self.database_name}")
            self.connection.close()
        
        # Return False to propagate any exceptions
        return False

def main():
    """
    Demonstrate the ExecuteQuery context manager with specific query requirements.
    """
    print("=== Reusable Query Context Manager Demo ===\n")
    
    # Execute the required query: SELECT * FROM users WHERE age > ? with parameter 25
    print("1. Executing query: SELECT * FROM users WHERE age > ? with parameter 25")
    with ExecuteQuery('users.db', "SELECT * FROM users WHERE age > ?", (25,)) as results:
        print("\nResults - Users older than 25:")
        print("-" * 60)
        for user in results:
            print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Age: {user[3]}")
    
    print("\n" + "="*60)
    
    # Demonstrate with another query to show reusability
    print("\n2. Demonstrating reusability with different query:")
    with ExecuteQuery('users.db', "SELECT name, age FROM users WHERE age >= ? ORDER BY age DESC", (40,)) as results:
        print("\nResults - Users 40 and older (sorted by age):")
        print("-" * 40)
        for user in results:
            print(f"Name: {user[0]}, Age: {user[1]}")
    
    print("\n" + "="*60)
    
    # Demonstrate with a simple query without parameters
    print("\n3. Simple query without parameters:")
    with ExecuteQuery('users.db', "SELECT COUNT(*) FROM users") as results:
        total_users = results[0][0]
        print(f"\nTotal number of users in database: {total_users}")

if __name__ == "__main__":
    main()
