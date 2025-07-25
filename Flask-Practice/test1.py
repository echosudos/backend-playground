from flask import Flask

app = Flask(__name__)

from markupsafe import escape

'''
@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"
'''


@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'