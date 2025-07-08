import time
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
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
"""
)
cursor.execute("INSERT INTO users (name) VALUES ('Alice')")
cursor.execute("INSERT INTO users (name) VALUES ('Bob')")
conn.commit()
conn.close()
# --- End of Setup ---


#### paste your with_db_connection decorator here
def with_db_connection(func):
    """
    Decorator that handles the database connection lifecycle (open/close).
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            result = func(conn, *args, **kwargs)
            return result
        finally:
            if conn:
                conn.close()

    return wrapper


def retry_on_failure(retries=3, delay=1):
    """
    A decorator factory that retries a function if it raises an exception.

    :param retries: The number of times to retry.
    :param delay: The number of seconds to wait between retries.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    # Attempt to execute the decorated function
                    return func(*args, **kwargs)
                except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
                    # Check if this is the last attempt
                    if attempt < retries - 1:
                        print(
                            f"RETRY: Attempt {attempt + 1}/{retries} failed: {e}. Retrying in {delay} second(s)..."
                        )
                        time.sleep(delay)
                    else:
                        print(
                            f"RETRY: Attempt {attempt + 1}/{retries} failed. All retries exhausted."
                        )
                        raise  # Re-raise the last exception

        return wrapper

    return decorator


# We need a counter to simulate failure for the demonstration
call_counter = 0


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_and_simulate_failure(conn):
    """
    Fetches users but is designed to fail the first two times it's called
    to demonstrate the retry decorator.
    """
    global call_counter
    call_counter += 1

    print(f"\nAttempting to execute function (call #{call_counter})...")

    # Simulate a transient error (e.g., "database is locked") on the first 2 attempts
    if call_counter <= 2:
        print("--> Simulating a failure...")
        raise sqlite3.OperationalError("database is locked")

    # Succeed on the 3rd attempt
    print("--> Success!")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


#### Attempt to fetch users with automatic retry on failure
print("--- Starting fetch operation with retry logic ---")
try:
    users = fetch_and_simulate_failure()
    print("\n--- Final Result ---")
    print("Successfully fetched users:", users)
except Exception as e:
    print("\n--- Final Result ---")
    print(f"Operation failed after all retries: {e}")


# --- Cleanup ---
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
