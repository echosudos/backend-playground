'''
Small Project #1

Skills and Tech Used:
- REST API Design
- JSON
- Basic Authentication middleware
- Flask
- Python Sqlite database
- Python

Objectives:
Main focus: CRUD operations. To Do List API with authentication logic, 
ability to create both users and tasks + update them + delete them and be 
able to retrieve a list of tasks and filter them by status and get details of
each one

Project Idea from: https://roadmap.sh/backend/project-ideas#2-to-do-list-api

Requirements to Run:
- Python 3.8
- pip install -r requirements.txt

References:
- https://flask-httpauth.readthedocs.io/en/latest/
- https://flask.palletsprojects.com/en/stable/quickstart/
'''
import sqlite3
from flask import Flask, request, jsonify, g
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


# ----------------------
# Initialize Application
# ----------------------
app = Flask(__name__)
auth = HTTPBasicAuth()

conn = sqlite3.connect('todo-database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('''
            CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
            )
            ''')
cur.execute ('''
            CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id)
            )
            ''')
    
conn.commit()


# ----------------------
# Routes ~ API Endpoints
# ----------------------
@app.route('/')
def index():
    return "Welcome to the ToDo List API!"

@app.route('/register', methods=['POST'])
def register():
    """
    Make a new user account
    Input JSON: {
        "username": "John",
        "password": "secret"
    }

    Output JSON: {
        "id": 1, 
        "username": "John"
    }
    """
    # Read JSON body of incoming request
    # Fallback: Empty Dict
    data: dict = request.get_json() or {}

    # Extract username and password from the data
    # Fallback: Empty String if username/password not found
    username: str = str(data.get('username', "")).strip()
    password: str = str(data.get('password', "")).strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if the username already exists
    cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
    if cur.fetchone():
        return jsonify({"error": "Username already exists"}), 409

    # Hash pasword
    hashed_password = generate_password_hash(password)

    # Insert new user into the database
    cur.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()

    # Get the ID of the newly created user
    user_id = cur.lastrowid
    return jsonify({"id": user_id, "username": username}), 201

@auth.verify_password
def verify_password(username, password):
    """
    Verify User Credentials

    Input: username, password
    Output: True if credentials are valid, False otherwise
    """

    # Check if username and password are provided
    if not username or not password:
        return False
    
    # Query the database for the user
    cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
    user = cur.fetchone()
    
    # If user exists and password matches, return True
    if user and check_password_hash(user['password'], password):
        # Set the current user in Flask's context
        g.current_user = user
        return True
    return False

@app.route('/tasks', methods=['GET', 'POST'])
@auth.login_required
def tasks():
    """
    Get or create tasks for the current user
    """
    if request.method == 'POST':
        # Create a new task
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')

        if not title or not description:
            return jsonify({"error": "Title and description are required"}), 400

        cur.execute("INSERT INTO Tasks (user_id, title, description, status, created_at) VALUES (?, ?, ?, ?, ?)",
                    (g.current_user['id'], title, description, 'pending', ''))
        conn.commit()
        return jsonify({"message": "Task created successfully"}), 201

    else:
        # Get all tasks for the current user
        cur.execute("SELECT * FROM Tasks WHERE user_id = ?", (g.current_user['id'],))
        tasks = cur.fetchall()
        return jsonify([dict(task) for task in tasks]), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)

    # Reset table contents on shutdown
    cur.execute("DELETE FROM Users")
    cur.execute("DELETE FROM Tasks")
    conn.commit()

    # Close Connection with Database
    conn.close()  
    cur.close()  
