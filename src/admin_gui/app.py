import sys
import os
import logging
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, send_from_directory, send_file, flash, session
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import sqlite3
from io import BytesIO
from flask_paginate import Pagination, get_page_parameter
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting the Admin GUI application...")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

logger.info("Flask app initialized")

# Use DATABASE_URL from environment variable, fallback to SQLite if not provided
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv('DATABASE_URL', os.path.join(current_dir, 'test_database.db'))
# Remove the 'sqlite:///' prefix if it exists
if DB_PATH.startswith('sqlite:///'):
    DB_PATH = DB_PATH[10:]
logger.info(f"Database path: {DB_PATH}")

def get_db_connection():
    try:
        logger.info(f"Attempting to connect to database at {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        logger.info("Database connection established")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_db():
    logger.info("Initializing database...")
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
        logger.info("Creating tables...")
        create_tables_path = os.path.join(current_dir, 'create_tables.sql')
        logger.info(f"Loading SQL from {create_tables_path}")
        with open(create_tables_path, 'r') as f:
            conn.executescript(f.read())
        
        # Insert default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if cursor.fetchone() is None:
            logger.info("Inserting default admin user...")
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

# Combined template
combined_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Admin GUI{% endblock %}</title>
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="{{ url_for('index') }}">Dashboard</a></li>
                <li><a href="{{ url_for('user_management') }}">User Management</a></li>
                <!-- Add more navigation items here -->
            </ul>
        </nav>
    </header>

    <main>
        {% block content %}
        <h1>Admin Dashboard</h1>

        <div class="dashboard">
            <div class="dashboard-item">
                <h2>User Management</h2>
                <p>Manage users, roles, and permissions.</p>
                <a href="{{ url_for('user_management') }}" class="button">Go to User Management</a>
            </div>
            <div class="dashboard-item">
                <h2>System Health</h2>
                <p>Monitor system performance and status.</p>
                <a href="#" class="button">View System Health</a>
            </div>
            <div class="dashboard-item">
                <h2>Logs</h2>
                <p>View and analyze system logs.</p>
                <a href="#" class="button">View Logs</a>
            </div>
        </div>
        {% endblock %}
    </main>

    <footer>
        <p>&copy; 2024 Admin GUI. All rights reserved.</p>
    </footer>
</body>
</html>
"""

@app.route('/')
def index():
    logger.info("Received request for index page")
    return render_template_string(combined_template)

@app.route('/user_management')
def user_management():
    logger.info("Received request for user management page")
    user_management_template = combined_template.replace(
        '{% block content %}',
        '{% block content %}<h1>User Management</h1><p>This page is under construction. User management features will be implemented here.</p>'
    )
    return render_template_string(user_management_template)

if __name__ == '__main__':
    logger.info("Entering main block")
    if init_db():
        debug_mode = os.getenv('DEBUG', 'False') == 'True'
        logger.info(f"Debug mode: {debug_mode}")
        logger.info("About to start Flask app")
        app.run(debug=debug_mode, host='0.0.0.0', port=5000)
    else:
        logger.error("Failed to initialize the database. Application not started.")

logger.info("Script execution completed")
