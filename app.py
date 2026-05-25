from flask import Flask, render_template, request, redirect
import sqlite3
import random
import string

app = Flask(__name__)

# DATABASE SETUP
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS urls(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        long_url TEXT,
        short_code TEXT
    )
    """)

    conn.commit()
    conn.close()


# SHORT CODE GENERATOR
def generate_code():
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(5))

# HOME ROUTE
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        long_url = request.form["url"]
        short_code = generate_code()

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO urls (long_url, short_code) VALUES (?, ?)",
            (long_url, short_code)
        )

        conn.commit()
        conn.close()

        short_url = request.host_url + short_code

        return render_template("index.html", short_url=short_url)

    return render_template("index.html")

# REDIRECT ROUTE
@app.route("/<code>")
def redirect_url(code):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT long_url FROM urls WHERE short_code=?",
        (code,)
    )

    result = cur.fetchone()
    conn.close()

    if result:
        return redirect(result[0])

    return "URL not found"

# RUN APP
init_db()
if __name__ == "__main__":
    app.run(debug=False)