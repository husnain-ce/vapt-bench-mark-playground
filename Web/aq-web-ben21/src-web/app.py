import os
import secrets
import sqlite3
import requests
from flask import Flask, request, session, render_template, make_response
from werkzeug.security import generate_password_hash, check_password_hash


DB_NAME = "database.db"
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex()


def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                """CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )"""
            )
            print("✅ Database initialized")


@app.after_request
def add_csp_header(response):
    response.headers['Content-Security-Policy'] = "default-src 'none'; style-src 'self';"
    return response


@app.route("/dashboard", methods=['GET'])
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return "User not logged", 400

    username = None
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        username = user[0] if user else None

    rendered = render_template("dashboard.html", username=username)
    response = make_response(rendered)
    response.headers['X-User-' + username] = user_id

    # Future logic for saving books of each user
    # ...

    return response


@app.route("/report", methods=['GET', 'POST'])
def report():
    if request.method == 'GET':
        return render_template("report.html")

    # Visit
    url = request.form.get("url")
    if not url.startswith('http'):
        return "Error, send an HTTP url!"

    requests.post("http://bot:1337/visit", data={'url': url})
    return "Bot visiting the url"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "Username and password required", 400

    hashed_pw = generate_password_hash(password)
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        return "Successful", 201
    except sqlite3.IntegrityError:
        return "Username already exists", 409
    

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

    if user and check_password_hash(user[1], password):
        session["user_id"] = user[0]
        return "Go to /dashboard", 200
    else:
        return "Invalid username or password", 400


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user_id", None)
    return "Logged out"


@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=80)
