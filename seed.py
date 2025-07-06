import mysql.connector
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection
import os
import csv
import uuid

from dotenv import load_dotenv

load_dotenv() 

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
}
DB_NAME = os.getenv('DB_NAME')
TABLE_NAME = os.getenv('TABLE_NAME')

def connect_db():
    """ Connects to the MySQL database server """
    print("Attempting to connect to MySQL server...")
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to MySQL server.")
            return connection
    except errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Access denied. Check your username or password.")
        return None
    except errorcode.ER_BAD_DB_ERROR:
        print("Error: Database does not exist.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
def create_database(connection: MySQLConnection):
    """ Creates the database ALX_prodev if it does not exist """
    if not connection:
        print("Cannot create database: No connection to server.")
        return
        
    cursor = connection.cursor()
    try:
        # 'IF NOT EXISTS' prevents an error if the DB already exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' is ready.")
    except mysql.connector.Error as err:
        print(f"Failed to create database: {err}")
    finally:
        cursor.close()

def connect_to_prodev():
    """ Connects to the ALX_prodev database in MYSQL """
    print(f"Attempting to connect to database '{DB_NAME}'...")
    try:
        # Add the database name to our config
        db_specific_config = DB_CONFIG.copy()
        db_specific_config['database'] = DB_NAME
        
        connection = mysql.connector.connect(**db_specific_config)
        if connection.is_connected():
            print(f"Successfully connected to database '{DB_NAME}'.")
            return connection
    except Exception as e:
        print(f"Failed to connect to '{DB_NAME}': {e}")
        return None
    
def create_table(connection: MySQLConnection):
    """ Creates a table user_data if it does not exist """
    if not connection:
        print("Cannot create table: No connection to database.")
        return
        
    cursor = connection.cursor()
    # Note: UUIDs are stored as CHAR(36) in MySQL
    table_definition = (
        f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} ("
        "  `user_id` CHAR(36) NOT NULL PRIMARY KEY,"
        "  `name` VARCHAR(255) NOT NULL,"
        "  `email` VARCHAR(255) NOT NULL,"
        "  `age` DECIMAL(5, 2) NOT NULL,"
        "  INDEX `email_index` (`email`)" # Adding an index on email is good practice
        ") ENGINE=InnoDB"
    )
    try:
        print(f"Creating table '{TABLE_NAME}'...")
        cursor.execute(table_definition)
        print(f"Table '{TABLE_NAME}' is ready.")
    except mysql.connector.Error as err:
        print(f"Failed to create table: {err}")
    finally:
        cursor.close()

def insert_data(connection, data):
    """ Inserts data into the database if it does not already exist """
    if not connection:
        print("Cannot insert data: No connection to database.")
        return
        
    cursor = connection.cursor()
    insert_query = (
        f"INSERT INTO {TABLE_NAME} (user_id, name, email, age) "
        "VALUES (%s, %s, %s, %s)"
    )
    
    for row in data:
        try:
            # Check if user with that email already exists to avoid duplicates
            cursor.execute(f"SELECT user_id FROM {TABLE_NAME} WHERE email = %s", (row['email'],))
            if cursor.fetchone():
                print(f"Skipping existing user: {row['email']}")
                continue

            # Generate a new UUID for the primary key
            user_id = str(uuid.uuid4())
            
            # Prepare data for insertion
            user_data = (user_id, row['name'], row['email'], row['age'])
            
            # Execute the insert query
            cursor.execute(insert_query, user_data)
            print(f"Inserted user: {row['name']}")
            
        except mysql.connector.Error as err:
            print(f"Failed to insert data for {row.get('name', 'N/A')}: {err}")
            
    # Commit the changes to the database
    connection.commit()
    print("Data insertion process complete.")
    cursor.close()

def main():
    """Main function to orchestrate the database setup and seeding."""
    # 1. Connect to the server and create the database
    server_conn = connect_db()
    if server_conn:
        create_database(server_conn)
        server_conn.close() # Close the general server connection
        print("Server connection closed.")
    else:
        print("Could not establish server connection. Exiting.")
        return

    # 2. Connect to the specific database and create the table/insert data
    prodev_conn = connect_to_prodev()
    if prodev_conn:
        create_table(prodev_conn)
        
        # 3. Read data from CSV and insert
        try:
            with open('user_data.csv', mode='r', encoding='utf-8') as csvfile:
                # DictReader reads rows as dictionaries
                csv_reader = csv.DictReader(csvfile)
                data_to_insert = [row for row in csv_reader]
                insert_data(prodev_conn, data_to_insert)
        except FileNotFoundError:
            print("Error: user_data.csv not found in the current directory.")
            
        prodev_conn.close()
        print(f"Connection to '{DB_NAME}' closed.")
    else:
        print(f"Could not connect to database '{DB_NAME}'. Exiting.")


if __name__ == "__main__":
    main()

    