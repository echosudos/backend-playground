from flask import render_template
from flask import url_for
from flask import Flask

app = Flask(__name__)
from markupsafe import escape

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name="urmom"):
    return render_template('hello.html', person=name)