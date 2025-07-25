from flask import Flask
import sqlite3

# ----------------------
# Initialize Application
# ----------------------
app = Flask(__name__)


conn = sqlite3.connect('todo-database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('''
            CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
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
            created_at TEXT NOT NULL
            FOREIGN KEY (user_id) REFERENCES Users(id)
            )
            ''')

conn.commit()
