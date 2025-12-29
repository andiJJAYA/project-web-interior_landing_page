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

@app.route("/konsultasi", methods=["GET", "POST"])
def konsultasi():
    if request.method == "POST":
        nama = request.form["nama"]
        email = request.form["email"]
        pesan = request.form["pesan"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO konsultasi (nama, email, pesan) VALUES (%s, %s, %s)",
            (nama, email, pesan)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return render_template(
            "konsultasi.html",
            success="Pesan konsultasi berhasil dikirim!"
        )

    return render_template("konsultasi.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()
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

@app.route("/register", methods=["GET", "POST"])
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
            "INSERT INTO users (nama, email, password) VALUES (%s, %s, %s)",
            (nama, email, password)
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

@app.route("/akun", methods=["GET", "POST"])
@login_required
def akun():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        nama = request.form["nama"] # Menambahkan input nama
        alamat = request.form["alamat"]
        no_hp = request.form["no_hp"]
        umur = request.form["umur"]

        # Logika: Jika input kosong, di DB akan tersimpan sebagai NULL atau string kosong
        cursor.execute(
            """
            UPDATE users
            SET nama=%s, alamat=%s, no_hp=%s, umur=%s
            WHERE id_user=%s
            """,
            (nama, alamat, no_hp, umur, session["user_id"])
        )
        conn.commit()
        session["nama"] = nama 

    cursor.execute(
        "SELECT nama, email, alamat, no_hp, umur FROM users WHERE id_user=%s",
        (session["user_id"],)
    )
    user = cursor.fetchone()
    
    # ... (bagian query order tetap sama)
    cursor.execute(
        """
        SELECT layanan AS service_name, tanggal AS order_date
        FROM orders WHERE id_user=%s
        ORDER BY tanggal DESC LIMIT 1
        """,
        (session["user_id"],)
    )
    order = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("akun.html", user=user, order=order)

@app.route("/order", methods=["POST"])
@login_required
def order():
    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO orders
        (id_user, nama, no_telepon, alamat, tanggal, bank, harga, layanan)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            session["user_id"],
            data["nama"],
            data["telepon"],
            data["alamat"],
            data["tanggal"],
            data["bank"],
            data["harga"],
            data["layanan"]
        )
    )

    conn.commit()
    cursor.close()
    conn.close()

    return "", 200

@app.route("/service/kitchen")
@login_required
def kitchen():
    return render_template("service_kitchen.html")

@app.route("/service/living-room")
@login_required
def living_room():
    return render_template("service_living.html")

@app.route("/service/workspace")
@login_required
def workspace():
    return render_template("service_workspace.html")

if __name__ == "__main__":
    app.run(debug=True)
