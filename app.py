from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For sessions

# ---------- Database Setup ----------
def create_connection():
    try:
        conn = sqlite3.connect("database.db")
        return conn
    except Error as e:
        print(e)
    return None

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_table()

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    # Input validation
    if not name or not age.isdigit() or int(age) <= 0 or not email or len(password) < 8:
        return "Invalid input data. Please check all fields.", 400

    hashed_password = generate_password_hash(password)

    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, age, email, password) VALUES (?, ?, ?, ?)",
                       (name, int(age), email, hashed_password))
        conn.commit()
        conn.close()
        session['user_email'] = email
        return "Registration successful!"
    except sqlite3.IntegrityError:
        return "Email already exists.", 400
    except Exception as e:
        print(e)
        return "Failed to save data. Please try again later.", 500

if __name__ == "__main__":
    app.run(debug=True)