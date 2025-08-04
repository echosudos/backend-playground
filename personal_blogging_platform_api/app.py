'''
Small Project #2

Skills/Tech/Concepts Explored
- REST API Design
- Flask
- Python Sqlite database
- Python

Objectives:
Make an API capable of
- Returning a list of articles. You can add filters such as publishing date, or tags
- Returning a single article, specified by the ID of the article
- Creating a new article to be published
- Deleting a single article, specified by the ID
- Updating a single article, again, you'd specify the article using its ID

Project Idea From: https://roadmap.sh/backend/project-ideas

App developed with:
- Python 3.8

Install Dependencies with pip install -r requirements.txt
'''

import sqlite3
from datetime import datetime
from flask import Flask, request, g, jsonify, abort

# ---- Init ----
app = Flask(__name__)

conn = sqlite3.connect('articles.db')
cur = conn.cursor()

cur.execute("DELETE FROM Articles")
cur.commit()

cur.execute('''
            CREATE TABLE IF NOT EXISTS Articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

conn.commit()
conn.close()


# ---- Pre-Request and Post Reuqest Functions
@app.teardown_appcontext
def close_db(error):
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()

@app.before_request
def before_request():
    if 'conn' not in g:
        g.conn = sqlite3.connect('articles.db')
        g.conn.row_factory = sqlite3.Row





