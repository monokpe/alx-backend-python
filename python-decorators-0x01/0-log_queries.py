import sqlite3
import functools
import os
from datetime import datetime

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
        name TEXT NOT NULL
    )
"""
)
cursor.execute("INSERT INTO users (name) VALUES ('Alice')")
cursor.execute("INSERT INTO users (name) VALUES ('Bob')")
conn.commit()
conn.close()
# --- End of Setup ---


#### decorator to log SQL queries
def log_queries(func):
    """
    A decorator that logs the SQL query passed to the decorated function
    before executing it.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find the query in the function's arguments
        # It could be a positional or a keyword argument.
        query_arg = None
        if "query" in kwargs:
            query_arg = kwargs["query"]
        elif args:
            query_arg = args[0]

        if query_arg:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f'LOG [{timestamp}]: Executing query: "{query_arg}"')
        else:
            print("LOG: Could not find query to log.")

        # Execute the original function and get the result
        result = func(*args, **kwargs)

        # Return the original function's result
        return result

    return wrapper


@log_queries
def fetch_all_users(query):
    """Fetches all users from the database using the provided query."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


#### fetch users while logging the query
print("Fetching users...")
users = fetch_all_users(query="SELECT * FROM users")
print("Fetched results:")
print(users)

# --- Cleanup ---
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
