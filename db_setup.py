import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database credentials from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connect to MySQL
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)

cursor = conn.cursor()

# Create database and tables
# cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
# conn.database = DB_NAME

# Recipes table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS recipes (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     description TEXT NOT NULL,
#     ingredients TEXT NOT NULL,
#     price FLOAT NOT NULL
# )
# """)

# # Users table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS users (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     email VARCHAR(60) NOT NULL UNIQUE,
#     password VARCHAR(255) NOT NULL
# )
# """)

# # Cart table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    user_id INT unique,
    items TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

print("Database and tables created successfully.")
cursor.close()
conn.close() 