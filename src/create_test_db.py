import sqlite3
import random
from datetime import datetime, timedelta
import json

def create_test_database():
    conn = sqlite3.connect('test_database.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT,
        role TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        summary TEXT,
        description TEXT,
        status TEXT,
        assignee_id INTEGER,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (assignee_id) REFERENCES users (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY,
        task_id INTEGER,
        user_id INTEGER,
        content TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY,
        content TEXT,
        metadata TEXT,
        created_at TIMESTAMP
    )
    ''')

    # Insert dummy data
    users = [
        (1, 'alice', 'alice@example.com', 'developer'),
        (2, 'bob', 'bob@example.com', 'manager'),
        (3, 'charlie', 'charlie@example.com', 'designer'),
        (4, 'david', 'david@example.com', 'tester'),
        (5, 'eve', 'eve@example.com', 'developer')
    ]
    cursor.executemany('INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)', users)

    tasks = [
        (1, 'Implement login functionality', 'Create a secure login system with password hashing', 'In Progress', 1, '2023-01-01 10:00:00', '2023-01-02 14:30:00'),
        (2, 'Design new logo', 'Create a modern logo for our brand', 'To Do', 3, '2023-01-02 09:00:00', '2023-01-02 09:00:00'),
        (3, 'Fix pagination bug', 'The pagination on the search results page is not working correctly', 'In Progress', 5, '2023-01-03 11:00:00', '2023-01-04 16:45:00'),
        (4, 'Write API documentation', 'Document all endpoints of our RESTful API', 'To Do', 2, '2023-01-04 13:00:00', '2023-01-04 13:00:00'),
        (5, 'Perform security audit', 'Conduct a thorough security audit of our systems', 'To Do', 4, '2023-01-05 10:00:00', '2023-01-05 10:00:00')
    ]
    cursor.executemany('INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?)', tasks)

    comments = [
        (1, 1, 1, 'Started working on the login form', '2023-01-01 11:30:00'),
        (2, 1, 2, 'Remember to use bcrypt for password hashing', '2023-01-01 13:45:00'),
        (3, 2, 3, 'I\'ve prepared some initial sketches', '2023-01-02 10:15:00'),
        (4, 3, 5, 'I think I found the issue, working on a fix', '2023-01-03 14:20:00'),
        (5, 4, 2, 'Please use OpenAPI specification for the documentation', '2023-01-04 15:00:00')
    ]
    cursor.executemany('INSERT OR REPLACE INTO comments VALUES (?, ?, ?, ?, ?)', comments)

    kb_entries = [
        (1, 'How to reset your password', '{"category": "User Guide", "tags": ["password", "account"]}', '2023-01-01 09:00:00'),
        (2, 'Best practices for code reviews', '{"category": "Development", "tags": ["code review", "best practices"]}', '2023-01-02 11:30:00'),
        (3, 'Company vacation policy', '{"category": "HR", "tags": ["vacation", "policy"]}', '2023-01-03 14:45:00'),
        (4, 'Setting up the development environment', '{"category": "Development", "tags": ["setup", "environment"]}', '2023-01-04 10:20:00'),
        (5, 'Customer support guidelines', '{"category": "Support", "tags": ["customer service", "guidelines"]}', '2023-01-05 16:00:00')
    ]
    cursor.executemany('INSERT OR REPLACE INTO knowledge_base VALUES (?, ?, ?, ?)', kb_entries)

    conn.commit()
    conn.close()

    print("Test database created successfully.")

if __name__ == "__main__":
    create_test_database()