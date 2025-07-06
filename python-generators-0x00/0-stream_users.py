import mysql.connector
import time
import os
from dotenv import load_dotenv

load_dotenv()

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}


def stream_users():
    """
    A generator that connects to the database and streams rows one by one
    using a server-side cursor.
    """
    connection = None
    try:
        # Establish connection
        connection = mysql.connector.connect(**DB_CONFIG)

        print("Connection established. Creating server-side cursor.")
        # The key to streaming: buffered=False creates a server-side cursor.
        # It fetches rows only when requested, not all at once.
        cursor = connection.cursor(buffered=False)

        # Execute the query
        query = "SELECT name, email, age FROM user_data ORDER BY name"
        cursor.execute(query)
        print("Query executed. Starting to stream rows...")

        # Yield rows one by one
        for row in cursor:
            yield row  # 'yield' makes this function a generator

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        # Ensure resources are always released
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nCursor and connection closed.")


def main():
    """Demonstrates the use of the data streaming generator."""
    print("--- Starting Database Stream ---")

    # Get the generator object
    row_generator = stream_users()

    # Iterate through the generator to get rows one by one
    row_count = 0
    for user_row in row_generator:
        row_count += 1
        print(
            f"  > Fetched Row {row_count}: Name={user_row[0]}, Email={user_row[1]}, Age={user_row[2]}"
        )
        # We add a small delay to simulate processing and make the streaming obvious
        time.sleep(0.5)

    print(f"\n--- Stream Complete. Total rows processed: {row_count} ---")


if __name__ == "__main__":
    main()
