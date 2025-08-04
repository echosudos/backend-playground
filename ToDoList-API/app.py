'''
Small Project #1

Skills/Tech/Concepts Explored
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


Things to explore further as of Aug 3, 2025
- g
- abort
- sqlite3
'''
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash





# ----------------------
# Initialize Application
# ----------------------
app = Flask(__name__)
auth = HTTPBasicAuth()

# Init DB connection
conn = sqlite3.connect('todo-database.db')
cur = conn.cursor()

# Reset Table
cur.execute("DELETE FROM Users")
cur.execute("DELETE FROM Tasks")
conn.commit()

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
conn.close()

# Creates a DB connection and stores it in Flask's context
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('todo-database.db')
        g.db.row_factory = sqlite3.Row
    return g.db

# ----------------------
# Routes ~ API Endpoints
# ----------------------
# Closes DB connection at the end of each req
@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return "Welcome to the ToDo List API!", 200

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
    # Initialize DB connection
    conn = get_db()  
    cur = conn.cursor()
    
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
    # Initialize DB connection
    conn = get_db()  
    cur = conn.cursor()

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
    # Initialize DB connection
    conn = get_db()  
    cur = conn.cursor()

    user_id = g.current_user['id'] # Get the current user's ID from the Flask context

    if request.method == 'POST':
        # Create a new task
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()

        if not title or not description:
            return jsonify({"error": "Title and description are required"}), 400

        now = datetime.now().isoformat()  # Get current time in ISO format
        cur.execute("INSERT INTO Tasks (user_id, title, description, status, created_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, title, description, 'pending', now))
        conn.commit()
        return jsonify({"message": "Task created successfully"}), 201

    # ---- Get All Tasks ----
    # Filtering tasks by Status via Query Parameter
    status_filter = request.args.get('status')
    if status_filter:
        cur.execute(
            "SELECT * FROM Tasks WHERE user_id = ? AND status = ?",
            (user_id, status_filter)
        )
    else:
        cur.execute(
            "SELECT * FROM Tasks WHERE user_id = ?",
            (user_id,)
        )
    
    rows = cur.fetchall()

    tasks = [dict(r) for r in rows]
    return jsonify(tasks), 200

@app.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def task(task_id):
    """
    Get: Return specified task for current user
    Put: Update fields of the specified task
    Delete: Delete the specified task
    """
    # Initialize DB connection
    conn = get_db()  
    cur = conn.cursor()

    user_id = g.current_user['id']

    # Get the task
    cur.execute(
        "SELECT * FROM Tasks WHERE id =? AND user_id =?",
        (task_id, user_id)
    )
    row = cur.fetchone()

    if not row:
        abort(404, description="Task not found")

    # Convert row to dict
    task = dict(row)

    if request.method == 'GET':
        # Return task as JSON
        return jsonify(task), 200
    
    if request.method == 'PUT':
        data = request.get_json() or {}
        # Update task fields
        title = data.get('title', task['title']).strip()
        description  = data.get('description', task['description']).strip()
        status  = data.get('status', task['status']).strip()

        # Update Timestamp
        now = datetime.now().isoformat()

        # Update task in database
        cur.execute(
            """
            UPDATE Tasks
            SET title       = ?,
                description = ?,
                status      = ?,
                created_at  = ?
            WHERE id = ? AND user_id = ?
            """,
            (title, description, status, now, task_id, user_id)
        )
        conn.commit()

        # Return the updated record in the response
        task.update({"title": title, "description": desc, "status": stat, "created_at": now})
        return jsonify(task), 200

    if request.method == 'DELETE':
        # Remove the task from the database
        cur.execute(
            "DELETE FROM Tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
        conn.commit()

        # Return success msg
        return jsonify({"message": "Task deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
