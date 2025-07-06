import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}


def paginate_users(page_size, offset):
    """
    Fetches a single 'page' of users from the database.

    Args:
        page_size (int): The number of users to fetch (LIMIT).
        offset (int): The number of users to skip (OFFSET).

    Returns:
        list: A list of user data dictionaries for the requested page.
              Returns an empty list if no more users are found.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))

        users = cursor.fetchall()
        return users

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []  # Return an empty list on error
    finally:
        if connection and connection.is_connected():
            connection.close()


def lazy_paginate(page_size: int = 5):
    """
    A generator that lazily fetches pages of users from the database.
    It only fetches the next page when requested by the consumer.

    Args:
        page_size (int): The number of users per page.

    Yields:
        list: A list of user dictionaries representing a single page of data.
    """
    offset = 0

    # --- The One Loop: This will run until there are no more pages to fetch ---
    while True:
        print(
            f"\n[Generator] Attempting to fetch a page of size {page_size} at offset {offset}..."
        )

        # Call the helper function to get the next page of data
        page_of_users = paginate_users(page_size=page_size, offset=offset)

        # If the page is empty, there's no more data. Stop the generator.
        if not page_of_users:
            print("[Generator] No more users found. Stopping.")
            break  # Exit the while loop, which ends the generator

        # Yield the fetched page to the consumer and pause execution
        yield page_of_users

        # After yielding, update the offset for the *next* time we are called
        offset += page_size


def main():
    """Demonstrates the use of the lazy pagination generator."""
    PAGE_SIZE = 3

    print("--- Starting Lazy Pagination Demo ---")
    print(f"Each page will contain up to {PAGE_SIZE} users.")

    # Get the generator object. No database query has been made yet.
    page_generator = lazy_paginate(page_size=PAGE_SIZE)

    # Use enumerate to keep track of the page number
    for i, page in enumerate(page_generator, start=1):
        print(f"\n[Consumer] Received Page #{i}. Data:")
        for user in page:
            print(f"  - {user['name']} (Age: {user['age']})")

        # Simulate a user action, like clicking a "Next Page" button
        try:
            input("\n   >>> Press Enter to fetch the next page, or Ctrl+C to stop...")
        except KeyboardInterrupt:
            print("\n[Consumer] Stopping.")
            break

    print("\n--- Demo Complete ---")


if __name__ == "__main__":
    main()
