from flask import Flask
app = Flask(__name__)

@app.route("/<path:name>")
def hello(name):
    # ⚠️ Unsafe — for demo only
    return f"""
    <!doctype html>
    <html>
      <head><title>Demo</title></head>
      <body>
        Hello, {name}!
      </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
