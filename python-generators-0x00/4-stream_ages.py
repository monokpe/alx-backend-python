import mysql.connector
from decimal import Decimal

from dotenv import load_dotenv
import os

load_dotenv()

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}


def stream_user_ages():
    """
    A generator that connects to the database and yields each user's age
    one by one in a memory-efficient manner.

    Yields:
        Decimal: The age of a single user.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("[Generator] Connection opened. Streaming user ages...")

        # Use a server-side cursor for memory-efficient streaming
        cursor = connection.cursor(buffered=False)

        query = "SELECT age FROM user_data"
        cursor.execute(query)

        # --- Loop #1: Iterates through the database cursor one row at a time ---
        for row in cursor:
            # The row is a tuple, e.g., (Decimal('28.00'),). We yield the value.
            yield row[0]

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("[Generator] Stream finished. Connection closed.")


def calculate_average_age():
    """
    Calculates the average age of all users by consuming data from a generator,
    ensuring memory efficiency.

    Returns:
        Decimal: The calculated average age.
    """
    # Initialize state variables for the aggregation
    total_age = Decimal(0)
    user_count = 0

    print("[Calculator] Starting to process ages from the stream...")

    # Get the generator that streams ages
    age_generator = stream_user_ages()

    # --- Loop #2: Consumes ages from the generator one by one ---
    for age in age_generator:
        total_age += age
        user_count += 1
        # Optional: uncomment to see the step-by-step calculation
        # print(f"[Calculator] Processed age: {age}. Current Sum: {total_age}, Count: {user_count}")

    # Calculate the final average after the loop is done
    if user_count > 0:
        average = total_age / user_count
    else:
        average = Decimal(0)

    return average


def main():
    """Main function to orchestrate the calculation and print the result."""
    print("--- Starting Memory-Efficient Average Age Calculation ---")

    average_age = calculate_average_age()

    print("\n--- Calculation Complete ---")
    # Print the final result, formatted to two decimal places
    print(f"Average age of users: {average_age:.2f}")


if __name__ == "__main__":
    main()
