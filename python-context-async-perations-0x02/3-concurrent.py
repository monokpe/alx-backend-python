import asyncio
import aiosqlite
import os
import time

DB_FILE = "concurrent_users.db"

# --- 1. A Helper Function to Set Up a Dummy Database Asynchronously ---


async def setup_database():
    """Asynchronously creates and populates a test database."""
    # Clean up old DB file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        """
        )

        users_to_add = [
            (1, "Alice", 30),
            (2, "Bob", 55),
            (3, "Charlie", 25),
            (4, "Diana", 45),
            (5, "Eve", 60),
        ]
        await db.executemany(
            "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", users_to_add
        )
        await db.commit()
    print(f"--- Database '{DB_FILE}' created and populated. ---\n")


# --- 2. Asynchronous Functions to Fetch Data (Corrected) ---


async def async_fetch_users():
    """Fetches all users from the database asynchronously."""
    print("-> Starting `async_fetch_users`...")
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print("<- Finished `async_fetch_users`.")
            return results


# This function has been modified to have no parameters.
async def async_fetch_older_users():
    """Fetches users older than 40 from the database asynchronously."""
    age_limit = 40  # Age is hardcoded as per the check's expectation
    print(f"-> Starting `async_fetch_older_users` (age > {age_limit})...")
    query = "SELECT * FROM users WHERE age > ?"
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(query, (age_limit,)) as cursor:
            results = await cursor.fetchall()
            print(f"<- Finished `async_fetch_older_users` (age > {age_limit}).")
            return results


# --- 3. Main Function to Run Queries Concurrently ---


async def fetch_concurrently():
    """Sets up the DB and runs multiple fetch queries concurrently."""
    await setup_database()

    start_time = time.time()

    print("--- Gathering concurrent database tasks... ---")

    # Use asyncio.gather to run both coroutines concurrently.
    # The call to async_fetch_older_users() now has no arguments.
    results = await asyncio.gather(async_fetch_users(), async_fetch_older_users())

    # Unpack the results from the list returned by gather
    all_users_results, older_users_results = results

    end_time = time.time()

    print("\n--- Concurrent fetching complete. ---")
    print(f"Total execution time: {end_time - start_time:.4f} seconds\n")

    # Display the results
    print("Results from `async_fetch_users` (All Users):")
    for user in all_users_results:
        print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}")

    print("\nResults from `async_fetch_older_users` (Age > 40):")
    for user in older_users_results:
        print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}")

    # Clean up the created database file
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"\nCleaned up and removed '{DB_FILE}'.")


# --- 4. Entry Point to Run the Async Code ---

if __name__ == "__main__":
    # Ensure you have aiosqlite installed: pip install aiosqlite
    asyncio.run(fetch_concurrently())
