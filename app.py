from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from config import create_connection

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this in production

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
        return redirect("/dashboard")
    except Exception as e:
        print(e)
        return "Failed to register. Email may already exist.", 400

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return "Invalid input", 400

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, email, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[3], password):
        session['user_email'] = email
        session['user_name'] = user[0]
        session['user_age'] = user[1]
        return redirect("/dashboard")
    else:
        return "Invalid email or password", 400

@app.route("/dashboard")
def dashboard():
    if 'user_email' not in session:
        return redirect("/login")
    return render_template("dashboard.html",
                           name=session['user_name'],
                           age=session['user_age'],
                           email=session['user_email'])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
    
    
    
