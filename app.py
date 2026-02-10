from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "kisaan_sathi_secret"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

# Create table (runs once)
db = get_db()
db.execute("""
CREATE TABLE IF NOT EXISTS farmers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    mobile TEXT,
    email TEXT,
    password TEXT
)
""")
db.close()

# ---------- SIGNUP ----------
@app.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()
        db.execute(
            "INSERT INTO farmers(name, mobile, email, password) VALUES (?, ?, ?, ?)",
            (name, mobile, email, password)
        )
        db.commit()
        db.close()

        return redirect("/login")

    return render_template("signup.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")
        password = request.form.get("password")

        db = get_db()
        user = db.execute(
            "SELECT * FROM farmers WHERE (mobile=? OR email=?) AND password=?",
            (identifier, identifier, password)
        ).fetchone()
        db.close()

        if user:
            session["farmer_id"] = user[0]
            session["farmer_name"] = user[1]
            return redirect("/dashboard")
        else:
            return "Invalid login credentials"

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():

    # If not logged in → go to login page
    if "farmer_id" not in session:
        return redirect("/login")

    db = get_db()
    user = db.execute(
        "SELECT name, mobile, email FROM farmers WHERE id=?",
        (session["farmer_id"],)
    ).fetchone()
    db.close()

    return render_template(
        "dashboard.html",
        name=user[0],
        mobile=user[1],
        email=user[2]
    )


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
