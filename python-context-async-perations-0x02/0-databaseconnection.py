import sqlite3
import os

# --- 1. The Class-Based Context Manager ---


class DatabaseConnection:
    """
    A class-based context manager for handling database connections.
    It automatically opens the connection on entering the 'with' block
    and closes it upon exiting.
    """

    def __init__(self, db_name):
        """Initializes the context manager with the database name."""
        self.db_name = db_name
        self.connection = None
        print(f"DatabaseConnection object created for '{self.db_name}'.")

    def __enter__(self):
        """Opens the database connection when entering the 'with' block."""
        print(f"--> Entering context: Connecting to {self.db_name}...")
        try:
            self.connection = sqlite3.connect(self.db_name)
            print("    Connection successful.")
            return self.connection
        except sqlite3.Error as e:
            print(f"    Error connecting to database: {e}")
            raise  # Reraise the exception to halt execution if connection fails

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the database connection when exiting the 'with' block."""
        print("<-- Exiting context: Closing the connection.")
        if self.connection:
            self.connection.close()
            print("    Connection closed.")
        # If an exception occurred inside the 'with' block, it's passed here.
        # We are not suppressing the exception, so we return None (or False).
        if exc_type:
            print(f"    An exception of type {exc_type.__name__} occurred.")


# --- 2. A Helper Function to Set Up a Dummy Database ---


def setup_database(db_name="my_app.db"):
    """Creates a simple database with a 'users' table and populates it."""
    print("\n--- Setting up the database for the demo ---")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table (if it doesn't exist)
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """
    )

    # Insert some data
    users_to_add = [
        (1, "Alice", "alice@example.com"),
        (2, "Bob", "bob@example.com"),
        (3, "Charlie", "charlie@example.com"),
    ]
    cursor.executemany(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)", users_to_add
    )

    conn.commit()
    conn.close()
    print("--- Database setup complete ---\n")


# --- 3. Using the Context Manager ---

if __name__ == "__main__":
    DB_FILE = "my_app.db"

    # Ensure the database exists with some data
    setup_database(DB_FILE)

    print("--- Starting database operations using the context manager ---")

    try:
        # Use the context manager to handle the connection
        with DatabaseConnection(DB_FILE) as conn:
            print("    Inside 'with' block. The connection is open.")

            # The 'conn' variable is the connection object returned by __enter__
            cursor = conn.cursor()

            query = "SELECT * FROM users"
            print(f"    Executing query: '{query}'")

            cursor.execute(query)
            results = cursor.fetchall()

            print("\n    Query Results:")
            for row in results:
                print(f"      ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
            print()

    except Exception as e:
        print(f"An error occurred outside the context manager: {e}")

    print("--- Operations finished. The connection should be closed now. ---")

    # Clean up the created database file
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"\nCleaned up and removed '{DB_FILE}'.")
