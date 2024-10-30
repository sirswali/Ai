import sys
import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
import sqlite3
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
        
        conn.commit()
        logger.info("Database initialized successfully")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        return False
    finally:
        conn.close()

@app.route('/')
def index():
    logger.info("Received request for index page")
    return render_template('index.html')

@app.route('/users')
def users():
    logger.info("Redirecting to user management")
    return redirect(url_for('user_management'))

@app.route('/credentials')
def credentials():
    logger.info("Received request for credentials page")
    return render_template('credentials.html')

@app.route('/history')
def history():
    logger.info("Received request for history page")
    return render_template('history.html')

@app.route('/user_dashboard')
def user_dashboard():
    logger.info("Received request for user dashboard page")
    return render_template('user_dashboard.html')

@app.route('/query_solution', methods=['POST'])
def query_solution():
    query = request.form.get('query')
    # Here you would process the query and return results
    # For now, we'll just return a placeholder response
    return jsonify({"result": f"Query processed: {query}"})

@app.route('/user_management')
def user_management():
    logger.info("Received request for user management page")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    if conn is None:
        flash("Error connecting to the database", "error")
        return redirect(url_for('index'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM users LIMIT ? OFFSET ?", (per_page, offset))
    users = cursor.fetchall()
    conn.close()
    
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')
    
    return render_template('user_management.html', users=users, pagination=pagination)

@app.route('/system_health')
def system_health():
    logger.info("Received request for system health page")
    return render_template('admin_system_health.html')

@app.route('/view_logs')
def view_logs():
    logger.info("Received request for logs page")
    return render_template('access_logs.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

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
