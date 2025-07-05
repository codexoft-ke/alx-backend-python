#!/usr/bin/python3
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """
    Generator that yields batches of users from the user_data table.
    """
    connection = connect_to_prodev()
    if connection:
        cursor = connection.cursor(dictionary=True)
        offset = 0
        while True:
            cursor.execute("SELECT * FROM user_data LIMIT %s OFFSET %s", (batch_size, offset))
            rows = cursor.fetchall()
            if not rows:
                break  # < exits loop instead of using `return`
            yield rows  # yields a batch
            offset += batch_size
        cursor.close()
        connection.close()


def batch_processing(batch_size):
    """
    Processes and prints users over age 25 from batches.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
