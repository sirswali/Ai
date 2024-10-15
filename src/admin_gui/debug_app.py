import sys
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Create a path for the debug log file
debug_log_path = os.path.join(current_dir, 'debug_log.txt')

with open(debug_log_path, 'w') as debug_file:
    debug_file.write("Starting script execution\n")

    try:
        from flask import Flask
        debug_file.write("Flask imported successfully\n")
    except ImportError as e:
        debug_file.write(f"Error importing Flask: {e}\n")

    try:
        from flask_bcrypt import Bcrypt
        debug_file.write("Bcrypt imported successfully\n")
    except ImportError as e:
        debug_file.write(f"Error importing Bcrypt: {e}\n")

    try:
        from flask_wtf.csrf import CSRFProtect
        debug_file.write("CSRFProtect imported successfully\n")
    except ImportError as e:
        debug_file.write(f"Error importing CSRFProtect: {e}\n")

    try:
        import sqlite3
        debug_file.write("sqlite3 imported successfully\n")
    except ImportError as e:
        debug_file.write(f"Error importing sqlite3: {e}\n")

    try:
        from dotenv import load_dotenv
        debug_file.write("load_dotenv imported successfully\n")
    except ImportError as e:
        debug_file.write(f"Error importing load_dotenv: {e}\n")

    debug_file.write("All imports attempted\n")

    # Initialize Flask app
    try:
        app = Flask(__name__)
        debug_file.write("Flask app initialized\n")
    except Exception as e:
        debug_file.write(f"Error initializing Flask app: {e}\n")

    debug_file.write("Script execution completed\n")

print(f"Debug log written to: {debug_log_path}")
