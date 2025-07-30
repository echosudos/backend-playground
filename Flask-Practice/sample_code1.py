from flask import Flask, request, render_template_string, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-secure-random-value'  # needed for sessions

# In‑memory “databases”
users = {}               # username -> password_hash
user_guestbooks = {}     # username -> list of entries

#############
# Templates #
#############

REGISTER_FORM = """
{% extends "base" %}
{% block body %}
  <h2>Register</h2>
  <form method="post">
    Username: <input name="username"><br>
    Password: <input name="password" type="password"><br>
    <button type="submit">Sign Up</button>
  </form>
  <p>Already have an account? <a href="{{ url_for('login') }}">Log in</a></p>
{% endblock %}
"""

LOGIN_FORM = """
{% extends "base" %}
{% block body %}
  <h2>Login</h2>
  <form method="post">
    Username: <input name="username"><br>
    Password: <input name="password" type="password"><br>
    <button type="submit">Log in</button>
  </form>
  <p>New here? <a href="{{ url_for('register') }}">Register</a></p>
{% endblock %}
"""

GUESTBOOK_PAGE = """
{% extends "base" %}
{% block body %}
  <h2>{{ session.username }}’s Guestbook</h2>
  <ul>
    {% for entry in entries %}
      <li>{{ entry }}</li>
    {% else %}
      <li><em>No entries yet!</em></li>
    {% endfor %}
  </ul>
  <form method="post">
    Add entry: <input name="message">
    <button type="submit">Sign</button>
  </form>
{% endblock %}
"""

####################
# Helper Decorator #
####################

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

#############
# Endpoints #
#############

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in users:
            return "Username taken, go back and choose another.", 400
        users[u] = generate_password_hash(p)
        user_guestbooks[u] = []
        session['username'] = u
        return redirect(url_for('my_guestbook'))
    return render_template_string(REGISTER_FORM)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        h = users.get(u)
        if h and check_password_hash(h, p):
            session['username'] = u
            return redirect(url_for('my_guestbook'))
        return "Invalid credentials, try again.", 401
    return render_template_string(LOGIN_FORM)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/my_guestbook', methods=['GET', 'POST'])
@login_required
def my_guestbook():
    u = session['username']
    if request.method == 'POST':
        msg = request.form.get('message', '').strip()
        if msg:
            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_guestbooks[u].append(f"{ts}: {msg}")
        return redirect(url_for('my_guestbook'))
    entries = user_guestbooks.get(u, [])
    return render_template_string(GUESTBOOK_PAGE, entries=entries)

# Make base template available
app.jinja_env.globals['session'] = session

if __name__ == '__main__':
    # Run with: python app.py
    app.run(debug=True)
