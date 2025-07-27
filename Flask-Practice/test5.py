from flask import Flask, request, render_template_string, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# In‑memory storage for guestbook entries
guestbook_entries = []


LOGIN_FORM = """
  <h2>Login</h2>
  <form method="post">
    Username: <input name="username"><br>
    Password: <input name="password" type="password"><br>
    <button type="submit">Log in</button>
  </form>
"""

GUESTBOOK_PAGE = """
  <h2>Guestbook</h2>
  <ul>
    {% for entry in entries %}
      <li>{{ entry }}</li>
    {% else %}
      <li><em>No entries yet!</em></li>
    {% endfor %}
  </ul>
  <form method="post">
    Your name: <input name="name"><button type="submit">Sign</button>
  </form>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username', 'Anonymous')
        return f"<h3>Hello, {user}! You’ve been “logged in.”</h3><a href='/login'>Back</a>"
    else:
        return render_template_string(LOGIN_FORM)

@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        name = request.form.get('name', 'Anonymous')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        guestbook_entries.append(f"{name} signed at {timestamp}")
        # Redirect to GET so we don’t repost on refresh
        return redirect(url_for('guestbook'))
    else:
        return render_template_string(GUESTBOOK_PAGE, entries=guestbook_entries)

if __name__ == '__main__':
    app.run(debug=True)

