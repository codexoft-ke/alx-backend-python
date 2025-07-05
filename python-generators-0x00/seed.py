#!/usr/bin/python3
import mysql.connector
import csv
import uuid


def connect_db():
    """Connect to the MySQL server (not a specific database)"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_database(connection):
    """Create ALX_prodev database if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Database creation error: {err}")


def connect_to_prodev():
    """Connect to ALX_prodev database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Connection to ALX_prodev failed: {err}")
        return None


def create_table(connection):
    """Create user_data table if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL,
                INDEX(user_id)
            );
        """)
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Table creation error: {err}")


def insert_data(connection, csv_file):
    """Insert users from CSV file into user_data table if they don't already exist"""
    try:
        cursor = connection.cursor()
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = row.get('user_id') or str(uuid.uuid4())
                cursor.execute("""
                    SELECT 1 FROM user_data WHERE user_id = %s;
                """, (user_id,))
                if cursor.fetchone():
                    continue  # Skip if user already exists

                cursor.execute("""
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s);
                """, (user_id, row['name'], row['email'], row['age']))
        connection.commit()
        cursor.close()
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found.")
    except mysql.connector.Error as err:
        print(f"Insert error: {err}")
