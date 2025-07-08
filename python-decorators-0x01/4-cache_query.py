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
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
"""
)
cursor.execute("INSERT INTO users (id, name) VALUES (1, 'Alice')")
cursor.execute("INSERT INTO users (id, name) VALUES (2, 'Bob')")
conn.commit()
conn.close()
# --- End of Setup ---


# This decorator is required for the example to run
def with_db_connection(func):
    """Decorator that handles the database connection lifecycle."""

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


# Global cache dictionary
query_cache = {}


def cache_query(func):
    """
    A decorator that caches the result of a database query function.
    The cache key is the SQL query string.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine the cache key from the 'query' argument
        query_key = None
        if "query" in kwargs:
            query_key = kwargs["query"]
        # The 'conn' object is the first positional arg (args[0]),
        # so the query would be the second (args[1])
        elif len(args) > 1:
            query_key = args[1]

        if not query_key:
            # Cannot cache without a key, execute directly
            return func(*args, **kwargs)

        # Check if the result is already in the cache
        if query_key in query_cache:
            print(f'CACHE HIT: Returning cached result for query: "{query_key}"')
            return query_cache[query_key]

        # If not in cache, execute the function (cache miss)
        print(f'CACHE MISS: Executing query and caching result for: "{query_key}"')
        result = func(*args, **kwargs)

        # Store the new result in the cache
        query_cache[query_key] = result
        return result

    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    A function that fetches data from the DB.
    We'll add a small delay to simulate network/DB latency.
    """
    print("-> Executing DB query...")
    time.sleep(1)  # Simulate a slow query
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    print("-> DB query finished.")
    return results


#### ---- DEMONSTRATION ---- ####

# 1. First call will be a CACHE MISS
print("--- First Call ---")
start_time = time.time()
users = fetch_users_with_cache(query="SELECT * FROM users")
end_time = time.time()
print(f"Result: {users}")
print(f"Time taken: {end_time - start_time:.2f} seconds\n")

# 2. Second call with the same query will be a CACHE HIT
print("--- Second Call (same query) ---")
start_time = time.time()
users_again = fetch_users_with_cache(query="SELECT * FROM users")
end_time = time.time()
print(f"Result: {users_again}")
print(f"Time taken: {end_time - start_time:.4f} seconds (notice it's much faster!)\n")

print(f"--- Current Cache State ---")
print(query_cache)

# --- Cleanup ---
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
