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
'''
import helpers
from flask import Flask

# ----------------------
# Initialize Application
# ----------------------
app = Flask(__name__)
conn, cur = helpers.init_db()
helpers.create_tables(cur, conn)
