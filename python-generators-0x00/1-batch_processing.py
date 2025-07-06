import os
import mysql.connector
from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}

