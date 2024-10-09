from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, send_file, flash, session
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import sqlite3
import os
import logging
from io import BytesIO
from flask_paginate import Pagination, get_page_parameter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use DATABASE_URL from environment variable, fallback to SQLite if not provided
DB_PATH = os.getenv('DATABASE_URL', r'C:\Users\vdube\OneDrive - OpenBet\Documents\Notes\Ai\test_database.db')

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn is None:
        logger.error("Failed to initialize database")
        return False

    try:
        # Check if the database is already initialized
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is not None:
            logger.info("Database already initialized")
            return True

        # If not initialized, create the tables
        with open('src/admin_gui/create_tables.sql', 'r') as f:
            conn.executescript(f.read())
        
        # Insert default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if cursor.fetchone() is None:
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            cursor.execute("INSERT INTO users (username, email, password, role_id) VALUES (?, ?, ?, ?)",
                           ('admin', 'admin@example.com', hashed_password, 1))
        
        conn.commit()
        logger.info("Database initialized successfully")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        return False
    finally:
        conn.close()

# ... (rest of the code remains the same)

if __name__ == '__main__':
    if init_db():
        app.run(debug=os.getenv('DEBUG', 'False') == 'True')
    else:
        logger.error("Failed to initialize the database. Application not started.")