import sqlite3
import os

# --- 1. A Helper Function to Set Up a Dummy Database ---


def setup_database(db_name="users_with_age.db"):
    """Creates a database with a 'users' table including an 'age' column."""
    print("--- Setting up the database for the demo ---")
    if os.path.exists(db_name):
        os.remove(db_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table with an 'age' column
    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    """
    )

    # Insert some data with varying ages
    users_to_add = [
        (1, "Alice", "alice@example.com", 30),
        (2, "Bob", "bob@example.com", 22),
        (3, "Charlie", "charlie@example.com", 35),
        (4, "Diana", "diana@example.com", 25),  # Age is not > 25
    ]
    cursor.executemany(
        "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)", users_to_add
    )

    conn.commit()
    conn.close()
    print(f"--- Database '{db_name}' setup complete ---\n")


# --- 2. The Reusable Context Manager for Executing Queries ---


class ExecuteQuery:
    """
    A reusable context manager to connect to a database,
    execute a given query, and automatically close the connection.
    The result of the query is returned upon entering the context.
    """

    def __init__(self, db_name, query, params=()):
        """Initializes with database details and the query to execute."""
        self.db_name = db_name
        self.query = query
        self.params = params
        self.connection = None
        print(f"ExecuteQuery object created for '{self.db_name}'.")

    def __enter__(self):
        """Connects, executes the query, and returns the results."""
        print(f"--> Entering context: Connecting to DB and running query...")
        try:
            self.connection = sqlite3.connect(self.db_name)
            cursor = self.connection.cursor()

            print(f"    Executing: {self.query} with params {self.params}")
            cursor.execute(self.query, self.params)
            results = cursor.fetchall()
            print("    Query successful, returning results.")
            return results
        except sqlite3.Error as e:
            print(f"    Database error: {e}")
            # Ensure connection is closed even if execute fails
            if self.connection:
                self.connection.close()
            raise  # Reraise the exception

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures the database connection is closed upon exiting."""
        print("<-- Exiting context: Closing the connection.")
        if self.connection:
            self.connection.close()
            print("    Connection closed.")
        if exc_type:
            print(
                f"    An exception ({exc_type.__name__}) occurred inside the 'with' block."
            )


# --- 3. Using the Context Manager ---

if __name__ == "__main__":
    DB_FILE = "users_with_age.db"

    # Create the database and table for our example
    setup_database(DB_FILE)

    # Define the query and the parameters
    sql_query = "SELECT * FROM users WHERE age > ?"
    query_params = (
        25,
    )  # Note: parameters must be in a tuple, even if there's only one

    print("--- Using the ExecuteQuery context manager ---")

    # The 'with' statement handles everything: connect, execute, fetch, and close.
    # The 'user_results' variable receives the return value from __enter__().
    with ExecuteQuery(DB_FILE, sql_query, query_params) as user_results:
        print("\n    Inside 'with' block. Processing the results...")

        print("\n    Users with age greater than 25:")
        if user_results:
            for user in user_results:
                # user is a tuple: (id, name, email, age)
                print(f"      - ID: {user[0]}, Name: {user[1]}, Age: {user[3]}")
        else:
            print("      No users found matching the criteria.")
        print()

    print("--- Context block finished. Connection is now closed. ---")

    # Clean up the created database file
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"\nCleaned up and removed '{DB_FILE}'.")
