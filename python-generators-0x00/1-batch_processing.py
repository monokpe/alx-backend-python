import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}


def stream_users_in_batches(batch_size: int = 100):
    """
    A generator that connects to the database, fetches users, and yields them
    in batches (lists) of a specified size.

    Args:
        batch_size (int): The number of rows to include in each batch.

    Yields:
        list: A list of user data dictionaries.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print(f"Connection established. Fetching users in batches of {batch_size}...")

        # Use a server-side cursor that returns dictionaries
        cursor = connection.cursor(dictionary=True, buffered=False)

        query = "SELECT user_id, name, email, age FROM user_data ORDER BY name"
        cursor.execute(query)

        batch = []
        # --- Loop #1: Iterates through each row from the database cursor ---
        for row in cursor:
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch  # Yield the complete batch
                batch = []  # Reset for the next batch

        # After the loop, yield any remaining users in the last batch
        if batch:
            yield batch

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nDatabase connection closed.")


def batch_processing(batch_size: int):
    """
    Processes user data in batches, filtering for users over the age of 25.

    Args:
        batch_size (int): The size of batches to request from the streamer.
    """
    print("--- Starting Batch Processing ---")

    # Get the generator that will stream batches
    user_batch_generator = stream_users_in_batches(batch_size)

    batch_num = 0
    # --- Loop #2: Iterates through each BATCH yielded by the generator ---
    for batch in user_batch_generator:
        batch_num += 1
        print(f"\n---> Processing Batch #{batch_num} (Size: {len(batch)})")

        # --- Loop #3 (as list comprehension): Filters users within the current batch ---
        filtered_users = [user for user in batch if user.get("age", 0) > 25]

        print(f"Found {len(filtered_users)} users over the age of 25 in this batch:")
        if not filtered_users:
            print("  None.")
        else:
            for user in filtered_users:
                # The 'age' is a Decimal type from the DB, format it for nice printing
                print(f"  - Name: {user['name']}, Age: {user['age']:.0f}")

    print("\n--- Batch Processing Complete ---")


def main():
    """Main function to run the batch processing demonstration."""
    # Define the batch size. Try changing this value (e.g., to 3, 5, or 10)
    # to see how the output changes.
    BATCH_SIZE = 4
    batch_processing(BATCH_SIZE)


if __name__ == "__main__":
    main()
