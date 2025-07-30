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
from flask import Flask, request, jsonify
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



if __name__ == '__main__':
    app.run(debug=True, port=5000)
    conn.close()  # Close the database connection when the app stops
    cur.close()  # Close the cursor as well
