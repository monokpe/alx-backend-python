import sqlite3
import functools
import os

# --- Setup: Create a dummy database for the example ---
DB_FILE = "users.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
"""
)
cursor.execute(
    "INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')"
)
cursor.execute(
    "INSERT INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')"
)
conn.commit()
conn.close()
# --- End of Setup ---


def with_db_connection(func):
    """
    Decorator that handles the database connection lifecycle.
    It opens a connection, passes it as the first argument to the decorated
    function, and ensures the connection is closed afterwards.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            # 1. Open the database connection
            conn = sqlite3.connect(DB_FILE)
            print("INFO: DB Connection opened.")

            # 2. Call the original function, passing the new connection
            #    object as the first argument.
            result = func(conn, *args, **kwargs)

            # 3. Return the result from the original function.
            return result
        finally:
            # 4. This block always executes, ensuring the connection is closed.
            if conn:
                conn.close()
                print("INFO: DB Connection closed.")

    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetches a single user from the database by their ID.
    Expects a database connection object `conn` as its first argument.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


#### Fetch user by ID with automatic connection handling
print("Attempting to fetch user with id=1...")
user = get_user_by_id(user_id=1)
print("\nFetched User:")
print(user)


# --- Cleanup ---
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
