from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from functools import wraps

app = Flask(__name__)
app.secret_key = "interior_secret_key"

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/konsultasi")
@login_required
def konsultasi():
    return render_template("konsultasi.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id_user"]
            session["nama"] = user["nama"]
            return redirect("/")

        return render_template("login.html", error="Email atau password salah")

    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        nama = request.form["nama"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_user FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template("register.html", error="Email sudah terdaftar")

        cursor.execute(
            "INSERT INTO users (nama,email,password) VALUES (%s,%s,%s)",
            (nama,email,password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/akun")
@login_required
def akun():
    return render_template("akun.html")

# ⬇️ WAJIB ADA
if __name__ == "__main__":
    app.run(debug=True)
