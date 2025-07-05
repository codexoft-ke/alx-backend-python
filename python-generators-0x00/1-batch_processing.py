#!/usr/bin/python3
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """
    Generator that yields batches of users from user_data table.
    """
    connection = connect_to_prodev()
    if connection:
        cursor = connection.cursor(dictionary=True)
        offset = 0
        while True:
            cursor.execute(f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}")
            rows = cursor.fetchall()
            if not rows:
                break
            yield rows
            offset += batch_size
        cursor.close()
        connection.close()


def batch_processing(batch_size):
    """
    Filters and prints users over the age of 25 in batches.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if int(user['age']) > 25:
                print(user)
