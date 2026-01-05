from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from functools import wraps
from flask import jsonify


app = Flask(__name__)
app.secret_key = "interior_secret_key"

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("email") != "admin@gmail.com":
            return "Akses Ditolak: Anda bukan Admin", 403
        return f(*args, **kwargs)
    return decorated

# USER ROUTES ======================
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
            session["email"] = user["email"]
            
            if user["email"] == "admin@gmail.com":
                return redirect("/admin")
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

    # LOGIKA UPDATE PROFIL (Jika User klik Simpan)
    if request.method == "POST":
        nama = request.form["nama"]
        alamat = request.form["alamat"]
        no_hp = request.form["no_hp"]
        umur = request.form["umur"]

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

    # QUERY DATA USER
    cursor.execute(
        "SELECT nama, email, alamat, no_hp, umur FROM users WHERE id_user=%s",
        (session["user_id"],)
    )
    user = cursor.fetchone()
    
    # QUERY PESANAN TERBARU (Termasuk Kolom Status)
    cursor.execute(
        """
        SELECT layanan AS service_name, tanggal AS order_date, status 
        FROM orders WHERE id_user=%s
        ORDER BY created_at DESC LIMIT 1
        """,
        (session["user_id"],)
    )
    order = cursor.fetchone()

    # QUERY KONSULTASI (Mengambil semua pesan konsultasi user ini)
    cursor.execute(
        "SELECT * FROM konsultasi WHERE email=%s ORDER BY created_at DESC",
        (user['email'],)
    )
    konsultasi_list = cursor.fetchall()

    # QUERY BALASAN (Mengambil semua balasan admin/user untuk chat tersebut)
    cursor.execute("""
        SELECT b.* FROM balas_konsultasi b 
        JOIN konsultasi k ON b.id_konsultasi = k.id_konsultasi 
        WHERE k.email=%s ORDER BY b.created_at ASC
    """, (user['email'],))
    balasan_list = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "akun.html", 
        user=user, 
        order=order, 
        konsultasi_list=konsultasi_list, 
        balasan_list=balasan_list
    )

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

@app.route("/admin")
@admin_required
def admin_dashboard():
    page = request.args.get('page', 'dashboard')
    conn = get_connection()
    cursor = conn.cursor()
    
    data = {}
    if page == 'dashboard':
        cursor.execute("SELECT COUNT(*) as total FROM users")
        data['total_users'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM orders")
        data['total_orders'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM konsultasi")
        data['total_konsultasi'] = cursor.fetchone()['total']
    elif page == 'orders':
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
        data['orders'] = cursor.fetchall()
    elif page == 'konsultasi':
        cursor.execute("SELECT * FROM konsultasi ORDER BY created_at DESC")
        data['konsultasi'] = cursor.fetchall()
    elif page == 'users':
        cursor.execute("SELECT id_user, nama, email, no_hp, alamat FROM users")
        data['users'] = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template("admin.html", page=page, data=data)

# ADMIN ROUTES ======================
@app.route("/admin/update_order/<int:id_order>/<action>")
@admin_required
def update_order(id_order, action):
    new_status = "Diterima" if action == "terima" else "Dibatalkan"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status=%s WHERE id_order=%s",
        (new_status, id_order)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin?page=orders")

@app.route("/admin/balas_konsultasi", methods=["POST"])
@admin_required
def admin_balas():
    id_konsultasi = request.form["id_konsultasi"]
    pesan = request.form["pesan_balas"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM balas_konsultasi WHERE id_konsultasi=%s", (id_konsultasi,))
    count = cursor.fetchone()['total']

    cursor.execute(
        "INSERT INTO balas_konsultasi (id_konsultasi, pengirim, pesan_balas) VALUES (%s, %s, %s)",
        (id_konsultasi, 'admin', pesan)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/admin?page=konsultasi")

@app.route("/admin/delete_user/<int:id_user>")
@admin_required
def delete_user(id_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id_user=%s", (id_user,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/admin?page=users")

@app.route("/admin/edit_user", methods=["POST"])
@admin_required
def edit_user():
    id_user = request.form["id_user"]
    nama = request.form["nama"]
    email = request.form["email"]
    no_hp = request.form["no_hp"]
    alamat = request.form["alamat"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET nama=%s, email=%s, no_hp=%s, alamat=%s WHERE id_user=%s",
        (nama, email, no_hp, alamat, id_user)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/admin?page=users")

#api endpoints ======================
@app.route("/api/konsultasi", methods=["POST"])
def api_konsultasi():
    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO konsultasi (nama, email, pesan) VALUES (%s, %s, %s)",
        (data["nama"], data["email"], data["pesan"])
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Pesan konsultasi terkirim"
    }), 201

@app.route("/api/order", methods=["POST"])
@login_required
def api_order():
    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO orders
        (id_user, nama, no_telepon, alamat, tanggal, bank, harga, layanan)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
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

    return jsonify({
        "status": "success",
        "message": "Order berhasil dibuat"
    }), 201

if __name__ == "__main__":
    app.run(debug=True)