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
    Decorator that handles the database connection lifecycle (open/close).
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            print("INFO: DB Connection opened.")
            result = func(conn, *args, **kwargs)
            return result
        finally:
            if conn:
                conn.close()
                print("INFO: DB Connection closed.")

    return wrapper


def transactional(func):
    """
    Decorator that wraps a function in a database transaction.
    Commits if the function succeeds, rolls back if it fails.
    """

    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # The wrapped function executes here.
            # Any execute() call will implicitly start a transaction.
            result = func(conn, *args, **kwargs)
        except Exception as e:
            # If any exception occurs, roll back the transaction
            print(f"TRANSACTION: An error occurred. Rolling back... Error: {e}")
            conn.rollback()
            raise  # Re-raise the exception to inform the caller
        else:
            # If the function completes successfully, commit the transaction
            print("TRANSACTION: Succeeded. Committing changes.")
            conn.commit()
        return result

    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Updates a user's email. This operation will succeed."""
    print(f"ACTION: Attempting to update user {user_id} email to {new_email}")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    print(f"ACTION: Update for user {user_id} executed.")


@with_db_connection
@transactional
def failing_update(conn, user_id):
    """
    Tries to update a user's name to NULL, which will fail because
    the 'name' column has a NOT NULL constraint.
    """
    print(f"\nACTION: Attempting a failing update for user {user_id}")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ? WHERE id = ?", (None, user_id))
    print(f"ACTION: This line will not be reached.")


@with_db_connection
def get_user_by_id(conn, user_id):
    """Helper to fetch a user to verify results."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


#### ---- DEMONSTRATION ---- ####

# 1. Show initial state of User 1
print("--- Verifying Initial State ---")
user_initial = get_user_by_id(user_id=1)
print(f"Initial User 1: {user_initial}\n")


# 2. Run the successful update
print("--- Running a Successful Transaction ---")
update_user_email(user_id=1, new_email="alice.new@web.com")
print("\n--- Verifying State After Success ---")
user_after_success = get_user_by_id(user_id=1)
print(f"User 1 after successful update: {user_after_success}\n")


# 3. Run the failing update and catch the expected error
print("--- Running a Failing Transaction (to demonstrate rollback) ---")
try:
    failing_update(user_id=2)
except sqlite3.IntegrityError as e:
    print(f"\nCaught expected error: {e}")

print("\n--- Verifying State After Failure ---")
user_after_failure = get_user_by_id(user_id=2)
print(f"User 2 after failed update (should be unchanged): {user_after_failure}")


# --- Cleanup ---
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
