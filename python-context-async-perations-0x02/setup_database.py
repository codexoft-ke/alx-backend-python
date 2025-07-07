#!/usr/bin/env python3
"""
Setup script to create and populate the SQLite database for testing context managers and async operations.
"""

import sqlite3

def setup_database():
    """Create and populate the users database for testing."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data with varied ages for testing
    sample_users = [
        ('John Doe', 'john.doe@example.com', 30),
        ('Jane Smith', 'jane.smith@example.com', 25),
        ('Bob Johnson', 'bob.johnson@example.com', 45),
        ('Alice Brown', 'alice.brown@example.com', 28),
        ('Charlie Wilson', 'charlie.wilson@example.com', 52),
        ('Diana Miller', 'diana.miller@example.com', 27),
        ('Frank Davis', 'frank.davis@example.com', 41),
        ('Grace Garcia', 'grace.garcia@example.com', 31),
        ('Henry Lee', 'henry.lee@example.com', 48),
        ('Ivy Chen', 'ivy.chen@example.com', 23),
        ('Jack Brown', 'jack.brown@example.com', 55),
        ('Kate Wilson', 'kate.wilson@example.com', 33),
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO users (name, email, age) VALUES (?, ?, ?)',
        sample_users
    )
    
    conn.commit()
    conn.close()
    print("Database setup complete! Created users.db with sample data.")
    print("Sample data includes users with ages ranging from 23 to 55 for testing age-based queries.")

if __name__ == "__main__":
    setup_database()
