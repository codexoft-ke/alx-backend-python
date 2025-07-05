#!/usr/bin/python3
from seed import connect_to_prodev

def stream_user_ages():
    """
    Generator that yields user ages one by one.
    """
    connection = connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data")
    for (age,) in cursor:
        yield age
    cursor.close()
    connection.close()

def calculate_average_age():
    """
    Calculates and prints the average age of users using the age generator.
    """
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
    if count > 0:
        average = total_age / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("No users found.")
