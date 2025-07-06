# alx-airbnb-project-documentation
# alx-backend-python

# MySQL Database Setup and Data Seeder

This Python script provides a robust solution for setting up a MySQL database, creating a specified table, and populating it with data from a CSV file. It leverages environment variables for secure and flexible configuration.

## Features

* **Secure Configuration:** Database credentials and names are loaded from a `.env` file, preventing sensitive information from being hardcoded.
* **Database Creation:** Automatically creates the specified database if it doesn't already exist.
* **Table Management:** Creates a `user_data` table with `user_id` (UUID), `name`, `email`, and `age` fields, ensuring email uniqueness.
* **Data Seeding:** Reads user data from `user_data.csv` and inserts it into the `user_data` table, skipping duplicates based on email.
* **Error Handling:** Includes comprehensive error handling for common database connection and operation issues.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install mysql-connector-python python-dotenv
    ```
2.  **Create `.env` file:**
    Create a file named `.env` in the same directory as the script with your MySQL credentials:
    ```
    DB_USER=your_mysql_username
    DB_PASSWORD=your_mysql_password
    DB_HOST=127.0.0.1
    DB_NAME=ALX_prodev
    TABLE_NAME=user_data
    ```
    *Replace `your_mysql_username` and `your_mysql_password` with your actual MySQL root or administrative credentials.*

3.  **Prepare `user_data.csv`:**
    Create a `user_data.csv` file in the same directory with `name`, `email`, and `age` columns. Example:
    ```csv
    name,email,age
    John Doe,john.doe@example.com,30.5
    Jane Smith,jane.smith@example.com,24
    Alice Brown,alice.brown@example.com,45.2
    ```
